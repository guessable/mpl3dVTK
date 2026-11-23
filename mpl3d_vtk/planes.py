"""Textured image planes with depth-tested placement."""
import numpy as np
import vtk
from matplotlib.cm import ScalarMappable

from ._geometry import array, numeric, poly
from .scene import Graphic


class _ImageGraphic(Graphic):
    def __init__(self, ax, data, pixels, pixel_alpha, interpolation, **style):
        self._pixels = None
        self._image_shape = pixels.shape[:2]
        self._pixel_alpha = pixel_alpha
        self.texture = vtk.vtkTexture()
        self.texture.SetInterpolate(interpolation == "linear")
        self.texture.RepeatOff()
        self.texture.EdgeClampOn()
        self.texture.SetColorModeToDirectScalars()
        super().__init__(ax, data, **style)
        self.actor.SetTexture(self.texture)
        self.set_values(pixels)

    def set_values(self, values):
        values = np.asanyarray(values)
        if values.shape not in (self._image_shape, self._image_shape + (3,), self._image_shape + (4,)):
            raise ValueError("image values must match the original shape with optional RGB(A) channels")
        self._pixels = values
        ScalarMappable.set_array(self, values if values.ndim == 2 else None)
        if values.ndim == 2 and not self.norm.scaled():
            self.autoscale_None()
        else:
            self._refresh()
        return self

    def set_array(self, values):
        self.set_values(values)

    def _refresh(self, *_):
        if self._pixels is None:
            return
        image = self._pixels
        if image.ndim == 2:
            rgba = self.to_rgba(self.get_array(), bytes=True)
        else:
            if image.dtype.kind == "u" and image.dtype != np.uint8:
                image = image / np.iinfo(image.dtype).max
            if image.dtype != np.uint8:
                image = np.clip(image, 0, 1)
            rgba = self.to_rgba(image, bytes=True)
        if self._pixel_alpha is not None:
            rgba = rgba.copy()
            rgba[..., 3] = (rgba[..., 3] * self._pixel_alpha).round().astype(np.uint8)
        ny, nx = self._image_shape
        pixels = vtk.vtkImageData()
        pixels.SetDimensions(nx, ny, 1)
        pixels.GetPointData().SetScalars(array(rgba.reshape(-1, 4), "pixels"))
        self.texture.SetInputData(pixels)
        self.axes.stale = True


def plot_image_plane(self, image, *, extent=None, z=0., origin="lower",
                     interpolation="nearest", pixel_alpha=None, **style):
    """Draw scalar or RGB(A) pixels in the XY plane at z.

    Extent gives the outer pixel edges (left, right, bottom, top).
    """
    image = np.asanyarray(image)
    if (image.ndim not in (2, 3) or min(image.shape[:2]) < 1
            or (image.ndim == 3 and image.shape[-1] not in (3, 4))):
        raise ValueError("image must be a nonempty scalar or RGB(A) array")
    if interpolation not in ("nearest", "linear"):
        raise ValueError("interpolation must be 'nearest' or 'linear'")
    if origin not in ("lower", "upper"):
        raise ValueError("origin must be 'lower' or 'upper'")
    if pixel_alpha is not None:
        pixel_alpha = np.broadcast_to(numeric(pixel_alpha), image.shape[:2])
        if not np.all((pixel_alpha >= 0) & (pixel_alpha <= 1)):
            raise ValueError("pixel_alpha must be in [0, 1]")
    ny, nx = image.shape[:2]
    left, right, bottom, top = (-.5, nx - .5, -.5, ny - .5) if extent is None else extent
    if not np.isfinite([left, right, bottom, top, z]).all() or left == right or bottom == top:
        raise ValueError("extent and z must be finite and the extent must have nonzero area")
    xyz = [[left, bottom, z], [right, bottom, z], [right, top, z], [left, top, z]]
    data = poly(xyz, [[0, 1, 2, 3]])
    uv = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=np.float32)
    if origin == "upper":
        uv[:, 1] = 1 - uv[:, 1]
    data.GetPointData().SetTCoords(array(uv, "uv"))
    return _ImageGraphic(self, data, image, pixel_alpha, interpolation, **style)
