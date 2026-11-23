"""Point clouds, coordinate transforms, alpha shapes and volume ray casting."""
from pathlib import Path

import numpy as np
import vtk
from matplotlib.artist import Artist
from matplotlib.cm import ScalarMappable
from vtk.util.numpy_support import vtk_to_numpy

from ._geometry import numeric, output, poly, volume_arrays, volume_grid
from .charts import scatter3
from .scene import Graphic, _cmap, chart
from .vectors import quiver3


def _cloud(value):
    if isinstance(value,(str,Path)):
        readers = {".ply":vtk.vtkPLYReader,".vtp":vtk.vtkXMLPolyDataReader}
        path = Path(value)
        if path.suffix.lower() not in readers:
            raise ValueError("point cloud files must be PLY or VTP")
        if not path.is_file():
            raise FileNotFoundError(path)
        reader = readers[path.suffix.lower()]()
        reader.SetFileName(str(path))
        data = output(reader)
        rgb = data.GetPointData().GetScalars()
        return vtk_to_numpy(data.GetPoints().GetData()), None if rgb is None else vtk_to_numpy(rgb)
    xyz = np.asarray(getattr(value,"Location",value),dtype=float)
    if not xyz.ndim >= 2 or xyz.shape[-1] != 3:
        raise ValueError("point cloud coordinates must have shape (..., 3)")
    c = getattr(value,"Color",None)
    if c is not None:
        c = np.asarray(c)
        c = c.reshape(-1,3) if c.size else None
    return xyz.reshape(-1,3),c


@chart
def pcshow(points, colors=None, *, markersize=5, ax, **kwargs):
    xyz,rgb = _cloud(points)
    color = colors if colors is not None else (rgb if rgb is not None else xyz[:,2])
    if not isinstance(color,(str,tuple)) and color is not None:
        color = np.asarray(color)
        if color.ndim > 2:
            color = color.reshape(-1,color.shape[-1])
    return scatter3(ax,*xyz.T,float(markersize)**2,color,**kwargs)


@chart
def pcshowpair(first, second, *, markersize=5, ax, **kwargs):
    a = pcshow(ax,first,"#b5599b",markersize=markersize,**kwargs)
    b = pcshow(ax,second,"#48a271",markersize=markersize,**kwargs)
    return a,b


def _rotation_matrices(q):
    q = numeric(q)
    if q.shape[-2:] == (3,3):
        return q.reshape(-1,3,3)
    if q.ndim == 0 or q.shape[-1] != 4:
        raise ValueError("rotations must be (n, 4) wxyz quaternions or (n, 3, 3) matrices")
    q = q.reshape(-1,4)
    length = np.linalg.norm(q,axis=1,keepdims=True)
    if np.any(length == 0) or not np.isfinite(length).all():
        raise ValueError("rotation quaternions must be finite and nonzero")
    w,x,y,z = (q/length).T
    return np.stack((1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y),
                     2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x),
                     2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)),axis=-1).reshape(-1,3,3)


@chart
def plotTransforms(translations, rotations=None, *, frame_size=1., show_frame_labels=False, ax, **kwargs):
    """Draw coordinate triads from homogeneous matrices or translations and rotations."""
    t = numeric(translations)
    if rotations is None:
        if t.shape[-2:] != (4,4):
            raise ValueError("expected homogeneous (n,4,4) transforms")
        transforms = t.reshape(-1,4,4)
        t,r = transforms[:,:3,3], transforms[:,:3,:3]
    else:
        if t.ndim == 0 or t.shape[-1] != 3:
            raise ValueError("translations must have shape (n,3)")
        t,r = t.reshape(-1,3),_rotation_matrices(rotations)
        r = np.broadcast_to(r,(len(t),3,3))
    handles = [quiver3(ax,*t.T,*(r[:,:,i]*frame_size).T,0,**{"color":color,**kwargs})
               for i,color in enumerate(("#d9534f","#4eae64","#3367ba"))]
    if show_frame_labels in (True,"on"):
        for i,p in enumerate(t):
            handles[0].annotations.append(ax.text(*p,str(i+1)))
    return handles


@chart
def alphashape(points, alpha, *, ax, **kwargs):
    """Draw the boundary of the tetrahedral alpha complex of 3-D points."""
    p,_ = _cloud(points)
    if not np.isfinite(alpha) and alpha != np.inf or alpha <= 0:
        raise ValueError("alpha must be positive")
    delaunay = vtk.vtkDelaunay3D()
    if np.isfinite(alpha):
        delaunay.SetAlpha(alpha)
        delaunay.AlphaTrisOff()
        delaunay.AlphaLinesOff()
        delaunay.AlphaVertsOff()
    tet = output(delaunay,poly(p[np.isfinite(p).all(axis=1)]))
    surface = output(vtk.vtkDataSetSurfaceFilter(),tet)
    return Graphic(ax,surface,**{"color":"#5590b1","lighting":"gouraud",**kwargs})


class VolumeGraphic(Artist, ScalarMappable):
    """Matplotlib artist and color mappable for a VTK volume."""
    def __init__(self,ax,data,values,cmap,alphamap,rendering_style,clim):
        Artist.__init__(self)
        ScalarMappable.__init__(self,cmap=cmap)
        self.axes,self.data = ax,data
        self.mapper = vtk.vtkSmartVolumeMapper()
        self.mapper.SetInputData(data)
        self.actor = vtk.vtkVolume()
        self.actor.SetMapper(self.mapper)
        self.actor.GetProperty().SetInterpolationTypeToLinear()
        self._cdata_mapping = "scaled"
        modes = {"VolumeRendering":self.mapper.SetBlendModeToComposite,
                 "MaximumIntensityProjection":self.mapper.SetBlendModeToMaximumIntensity,
                 "MinimumIntensityProjection":self.mapper.SetBlendModeToMinimumIntensity,
                 "AverageIntensityProjection":self.mapper.SetBlendModeToAverageIntensity}
        if rendering_style not in modes:
            raise ValueError(f"unknown volume rendering style {rendering_style!r}")
        modes[rendering_style]()
        self._opacity = np.asarray(alphamap,dtype=float).ravel()
        if self._opacity.size < 2 or not np.all((self._opacity>=0)&(self._opacity<=1)):
            raise ValueError("AlphaMap must have at least two values in [0,1]")
        self.set_array(values)
        if clim is not None:
            self.set_clim(*clim)
        self.callbacks.connect("changed",self._refresh)
        self._refresh()
        ax.renderer.AddVolume(self.actor)
        ax.add_artist(self)
        ax.handles.append(self)
        ax._limits_dirty = True

    def _refresh(self,*_):
        colors = vtk.vtkColorTransferFunction()
        opacity = vtk.vtkPiecewiseFunction()
        lo,hi = self.get_clim()
        if lo == hi:
            hi = lo+1
        for t in np.linspace(lo,hi,256):
            colors.AddRGBPoint(t,*self.to_rgba(t)[:3])
        for t,a in zip(np.linspace(lo,hi,len(self._opacity)),self._opacity):
            opacity.AddPoint(t,a)
        self.actor.GetProperty().SetColor(colors)
        self.actor.GetProperty().SetScalarOpacity(opacity)
        self.axes.stale = True

    def raw_bounds(self):
        return self.data.GetBounds()

    def sync_geometry(self,transforms,nonlinear):
        if any(nonlinear):
            raise ValueError("volume rendering requires linear axes")
        self.actor.SetVisibility(self.get_visible())

    def remove(self):
        if self in self.axes.handles:
            self.axes.renderer.RemoveVolume(self.actor)
            self.axes.handles.remove(self)
            self.axes._limits_dirty = True
            super().remove()


@chart
def volshow(v, *, coords=None, cmap="gray", alphamap=(0.,0.,.45,.9),
            rendering_style="VolumeRendering", clim=None, ax):
    """Ray cast a scalar volume on a uniform rectilinear grid."""
    axes,v = volume_arrays((v,) if coords is None else (*coords,v))
    if not np.isfinite(v).all():
        raise ValueError("volshow requires finite scalar samples")
    data = volume_grid(axes,v,image=True)
    if not data.IsA("vtkImageData"):
        raise ValueError("volshow requires uniform and ascending coordinates")
    return VolumeGraphic(ax,data,v,_cmap(cmap),alphamap,rendering_style,clim)
