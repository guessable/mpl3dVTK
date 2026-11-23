"""Polygon meshes, gridded surfaces and contours."""
import numpy as np
import vtk

from ._geometry import array, iso_filter, levels as contour_levels, numeric, output, poly, surface_poly, vertices
from .scene import Graphic


def _normals(xyz):
    normals = np.cross(np.gradient(xyz, axis=1), np.gradient(xyz, axis=0))
    return normals / np.maximum(np.linalg.norm(normals, axis=-1, keepdims=True), 1e-30)


def _surface(ax, x, y, z, values, style):
    data = surface_poly(x, y, z)
    handle = Graphic(ax, data, z if values is None else values, **style)
    handle._surface_shape = z.shape
    handle._surface_xy_finite = np.isfinite(x).all() and np.isfinite(y).all()
    handle._surface_all_finite = handle._surface_xy_finite and np.isfinite(z).all()
    handle._color_tracks_height = values is None
    handle._update_surface_normals()
    return handle


def plot_mesh(self, vertices, faces, *, values=None, association="point", **style):
    """Draw a polygon mesh with zero-based indices into an (n, 3) vertex array.

    Set association to "cell" for one scalar or RGB(A) color per face.
    """
    if "color" not in style and "facecolor" not in style and values is None and "cmap" not in style:
        style["color"] = self._get_lines.get_next_color()
    return Graphic(self, poly(numeric(vertices), faces), values, association=association, **style)


def _contour(ax, x, y, z, *, levels=10, offset=None, **style):
    data = surface_poly(x, y, z)
    data.GetPointData().SetScalars(array(z.ravel(), "height"))
    levels = contour_levels(z, levels)
    lines = iso_filter(data, levels)
    if offset is not None and lines.GetNumberOfPoints():
        vertices(lines)[:, 2] = offset
        lines.GetPoints().Modified()
    join = vtk.vtkStripper()
    join.JoinContiguousSegmentsOn()
    handle = Graphic(ax, output(join, lines), **style)
    handle.contour_levels = np.unique(levels)
    return handle
