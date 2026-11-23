"""Point clouds, coordinate frames and volume ray casting."""
from pathlib import Path

import numpy as np
import vtk
from matplotlib.artist import Artist
from matplotlib.cm import ScalarMappable
from vtk.util.numpy_support import vtk_to_numpy

from ._geometry import numeric, output, poly, volume_arrays, volume_grid
from .scene import Graphic, _cmap


def _cloud(points):
    if isinstance(points, (str, Path)):
        path = Path(points)
        readers = {".ply": vtk.vtkPLYReader, ".vtp": vtk.vtkXMLPolyDataReader}
        reader_cls = readers.get(path.suffix.lower())
        if reader_cls is None:
            raise ValueError("point cloud files must be PLY or VTP")
        if not path.is_file():
            raise FileNotFoundError(path)
        reader = reader_cls()
        reader.SetFileName(str(path))
        data = output(reader)
        scalars = data.GetPointData().GetScalars()
        if not data.GetNumberOfPoints():
            return np.empty((0, 3)), None
        return vtk_to_numpy(data.GetPoints().GetData()), None if scalars is None else vtk_to_numpy(scalars)
    xyz = numeric(points)
    if xyz.ndim < 2 or xyz.shape[-1] != 3:
        raise ValueError("points must have shape (..., 3)")
    return xyz.reshape(-1, 3), None


def plot_point_cloud(self, points, *, c=None, s=25, **style):
    """Render an array of points or a PLY or VTP file as a point cloud."""
    xyz, file_colors = _cloud(points)
    if c is None and "color" not in style:
        c = file_colors if file_colors is not None else xyz[:, 2]
    return self.scatter(*xyz.T, s=s, c=c, **style)


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



def plot_coordinate_frames(self, translations, *, rotations=None, frame_size=1.,
                           show_labels=False, **style):
    """Draw triads from homogeneous transforms or from translations and rotations."""
    t = numeric(translations)
    if rotations is None:
        if t.shape[-2:] != (4, 4):
            raise ValueError("expected homogeneous transforms with shape (n, 4, 4)")
        transforms = t.reshape(-1, 4, 4)
        t, r = transforms[:, :3, 3], transforms[:, :3, :3]
    else:
        if t.ndim == 0 or t.shape[-1] != 3:
            raise ValueError("translations must have shape (n, 3)")
        t, r = t.reshape(-1, 3), _rotation_matrices(rotations)
        r = np.broadcast_to(r, (len(t), 3, 3))
    handles = [
        self.quiver(*t.T, *r[:, :, i].T, length=frame_size, **{"color": color, **style})
        for i, color in enumerate(("#d9534f", "#4eae64", "#3367ba"))
    ]
    if show_labels:
        handles[0].annotations.extend(self.text(*point, str(i)) for i, point in enumerate(t))
    return handles


def plot_alpha_shape(self, points, *, radius, **style):
    """Draw the boundary of the tetrahedral alpha complex of 3-D points."""
    p, _ = _cloud(points)
    if np.isnan(radius) or radius <= 0:
        raise ValueError("radius must be positive")
    delaunay = vtk.vtkDelaunay3D()
    if np.isfinite(radius):
        delaunay.SetAlpha(radius)
        delaunay.AlphaTrisOff()
        delaunay.AlphaLinesOff()
        delaunay.AlphaVertsOff()
    tet = output(delaunay,poly(p[np.isfinite(p).all(axis=1)]))
    surface = output(vtk.vtkDataSetSurfaceFilter(),tet)
    return Graphic(self, surface, **{"color": "#5590b1", "lighting": "gouraud", **style})



class VolumeGraphic(Artist, ScalarMappable):
    """Matplotlib artist and color mappable for a VTK volume."""

    def __init__(self, ax, data, values, *, cmap, norm, opacity, blend_mode, vmin, vmax, label):
        Artist.__init__(self)
        ScalarMappable.__init__(self, cmap=_cmap(cmap), norm=norm)
        self.axes, self.data = ax, data
        self.mapper = vtk.vtkSmartVolumeMapper()
        self.mapper.SetInputData(data)
        self.actor = vtk.vtkVolume()
        self.actor.SetMapper(self.mapper)
        self.actor.GetProperty().SetInterpolationTypeToLinear()
        modes = {
            "composite": self.mapper.SetBlendModeToComposite,
            "maximum": self.mapper.SetBlendModeToMaximumIntensity,
            "minimum": self.mapper.SetBlendModeToMinimumIntensity,
            "average": self.mapper.SetBlendModeToAverageIntensity,
        }
        if blend_mode not in modes:
            raise ValueError(f"unknown blend_mode {blend_mode!r}")
        modes[blend_mode]()
        self._opacity = numeric(opacity).ravel()
        if self._opacity.size < 2 or not np.all((self._opacity >= 0) & (self._opacity <= 1)):
            raise ValueError("opacity must have at least two values in [0, 1]")
        self.set_label(label)
        self.set_array(values)
        self.set_clim(vmin, vmax)
        self.callbacks.connect("changed", self._refresh)
        self._refresh()
        ax.renderer.AddVolume(self.actor)
        ax.add_artist(self)
        ax.handles.append(self)
        ax._limits_dirty = True

    def _refresh(self, *_):
        colors = vtk.vtkColorTransferFunction()
        opacity = vtk.vtkPiecewiseFunction()
        lo, hi = self.get_clim()
        if lo == hi:
            hi = lo + 1
        levels = np.linspace(lo, hi, 256)
        for level, rgb in zip(levels, self.to_rgba(levels)[:, :3]):
            colors.AddRGBPoint(level, *rgb)
        for level, alpha in zip(np.linspace(lo, hi, len(self._opacity)), self._opacity):
            opacity.AddPoint(level, alpha)
        self.actor.GetProperty().SetColor(colors)
        self.actor.GetProperty().SetScalarOpacity(opacity)
        self.axes.stale = True

    def set_visible(self, visible):
        super().set_visible(visible)
        self.actor.SetVisibility(bool(visible))

    def _raw_bounds(self):
        return self.data.GetBounds()

    _render_bounds = _raw_bounds

    def _sync_geometry(self, transforms, nonlinear):
        if any(nonlinear):
            raise ValueError("volume rendering requires linear axes")

    def remove(self):
        if self in self.axes.handles:
            self.axes.renderer.RemoveVolume(self.actor)
            self.axes.handles.remove(self)
            self.axes._limits_dirty = True
            super().remove()


def plot_volume(self, values, *, coordinates=None, cmap="gray", norm=None, vmin=None, vmax=None,
                opacity=(0., 0., .45, .9), blend_mode="composite", label=None):
    """Ray cast a scalar volume on a uniform rectilinear grid."""
    coords, values = volume_arrays(values, coordinates)
    if not np.isfinite(values).all():
        raise ValueError("volume rendering requires finite scalar samples")
    data = volume_grid(coords, values, image=True)
    if not data.IsA("vtkImageData"):
        raise ValueError("volume rendering requires uniformly spaced, ascending coordinates")
    return VolumeGraphic(self, data, values, cmap=cmap, norm=norm, opacity=opacity,
                         blend_mode=blend_mode, vmin=vmin, vmax=vmax, label=label)
