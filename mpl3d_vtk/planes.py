"""Image primitives rendered as a depth-tested textured plane."""
import numpy as np
import vtk
from matplotlib.cm import ScalarMappable

from ._geometry import array, numeric, poly
from .scene import Graphic, chart


def _edges(coordinates, count):
    if coordinates is None:
        return .5, count+.5
    centers = numeric(coordinates).ravel()
    if not len(centers) or not np.isfinite(centers).all():
        raise ValueError("image coordinates must be finite")
    first = centers[0]
    last = centers[-1] if len(centers) > 1 else first+count-1
    step = (last-first)/(count-1) if count > 1 else 1.
    if step == 0:
        raise ValueError("image extent cannot be zero")
    return first-step/2,last+step/2


class _ImageGraphic(Graphic):
    def __init__(self, ax, data, cdata, alpha_data, alpha_mapping, interpolation, **kwargs):
        self._pixels = None
        self._image_shape = cdata.shape[:2]
        self._image_alpha = alpha_data
        if interpolation not in ("nearest","linear"):
            raise ValueError("Interpolation must be nearest or linear")
        self.texture = vtk.vtkTexture()
        self.texture.SetInterpolate(interpolation == "linear")
        self.texture.RepeatOff()
        self.texture.EdgeClampOn()
        self.texture.SetColorModeToDirectScalars()
        super().__init__(ax,data,alphadatamapping=alpha_mapping,**kwargs)
        self.actor.SetTexture(self.texture)
        self.set_cdata(cdata)

    def set_cdata(self, values, *, _refresh=True):
        values = np.asanyarray(values)
        if values.ndim not in (2,3) or values.shape[:2] != self._image_shape:
            raise ValueError("CData must match the original image size")
        if values.ndim == 3 and values.shape[2] not in (3,4):
            raise ValueError("truecolor CData requires RGB or RGBA")
        self._pixels = values
        scalars = None
        if values.ndim == 2:
            scalars = numeric(values)
            if self._cdata_mapping == "direct":
                scalars = np.floor(scalars)
                if values.dtype.kind in "bui":
                    scalars += 1
        ScalarMappable.set_array(self,scalars)
        if _refresh:
            self._refresh()
        return self

    def _refresh(self, *_):
        if self._pixels is None:
            return
        v = self._pixels
        if v.ndim == 2:
            rgba = self.to_rgba(self.get_array(),bytes=True)
        else:
            if v.dtype.kind == "u":
                v = v/np.iinfo(v.dtype).max
            rgba = self.to_rgba(np.clip(v,0,1),bytes=True)
        ny,nx = self._image_shape
        alpha = np.broadcast_to(numeric(self._image_alpha),(ny,nx))
        if self._alpha_mapping == "scaled":
            lo,hi = self.axes.alpha_limits
            alpha = (alpha-lo)/(hi-lo)
        elif self._alpha_mapping == "direct":
            alpha = (alpha-1)/63
        rgba = rgba.copy()
        rgba[...,3] = (rgba[...,3]*np.nan_to_num(np.clip(alpha,0,1))).round().astype(np.uint8)
        pixels = vtk.vtkImageData()
        pixels.SetDimensions(nx,ny,1)
        pixels.GetPointData().SetScalars(array(rgba.reshape(-1,4),"pixels"))
        self.texture.SetInputData(pixels)
        self.axes.stale = True

    def set_alphadata(self, value):
        np.broadcast_to(value,self._image_shape)
        self._image_alpha = value
        self._refresh()


def _image(args, ax, z, mapping, kwargs):
    options = kwargs.copy()
    if len(args) in (2,4):
        args, limits = args[:-1],args[-1]
        options.setdefault("clim",limits)
    if len(args) == 3:
        x,y,c = args
    elif len(args) in (0,1):
        x = options.pop("xdata",None)
        y = options.pop("ydata",None)
        c = args[0] if args else options.pop("cdata",None)
    else:
        raise TypeError("expected C, X,Y,C, or CData")
    c = np.asanyarray(c)
    if c.ndim not in (2,3) or (c.ndim == 3 and c.shape[-1] not in (3,4)) or min(c.shape[:2]) < 1:
        raise ValueError("CData must be an M×N scalar or RGB(A) image")
    nx0,nx1 = _edges(x,c.shape[1])
    ny0,ny1 = _edges(y,c.shape[0])
    xyz = np.array([[nx0,ny0,z],[nx1,ny0,z],[nx1,ny1,z],[nx0,ny1,z]])
    data = poly(xyz,[[0,1,2,3]])
    data.GetPointData().SetTCoords(array(np.array([[0,0],[1,0],[1,1],[0,1]],dtype=np.float32),"uv"))
    alpha = options.pop("alphadata",1.)
    alpha_mapping = options.pop("alphadatamapping","none")
    interpolation = options.pop("interpolation","nearest")
    np.broadcast_to(alpha,c.shape[:2])
    use_top_view = not ax.handles and z == 0
    h = _ImageGraphic(ax,data,c,alpha,alpha_mapping,interpolation,
                      **{"cdatamapping":mapping,"edgecolor":"none",**options})
    if use_top_view:
        ax.set_view(0,90)
    return h


@chart
def image(*args, z=0., ax, **kwargs):
    """Display indexed or truecolor pixels in the XY plane."""
    return _image(args,ax,z,"direct",kwargs)


@chart
def imagesc(*args, z=0., ax, **kwargs):
    """Display an XY image with scaled scalar colors."""
    return _image(args,ax,z,"scaled",kwargs)
