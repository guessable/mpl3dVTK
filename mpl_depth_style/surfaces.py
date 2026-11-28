"""Surface and triangle mesh builders for VtkAxes."""
import numpy as np

from ._geometry import cells, coordinate_mesh, surface_cells
from .scene import Graphic


def _normals(xyz):
    normals = np.cross(np.gradient(xyz, axis=1), np.gradient(xyz, axis=0))
    lengths = np.einsum("...i,...i->...", normals, normals)
    np.sqrt(lengths, out=lengths)
    np.maximum(lengths, 1e-30, out=lengths)
    normals /= lengths[..., None]
    return normals


def _surface(ax, x, y, z, values, style):
    data = coordinate_mesh(x, y, z)
    finite_x, finite_y, finite_z = map(np.isfinite, (x, y, z))
    xy_finite = finite_x.all() and finite_y.all()
    all_finite = xy_finite and finite_z.all()
    valid = None if all_finite else finite_x & finite_y & finite_z
    data.SetPolys(surface_cells(z.shape, valid))
    handle = Graphic(ax, data, z if values is None else values, **style)
    handle._surface_shape = z.shape
    handle._surface_xy_finite = xy_finite
    handle._surface_all_finite = all_finite
    handle._color_tracks_height = values is None
    handle._update_surface_normals()
    return handle


def _triangle_arrays(x, y, triangles):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if x.ndim != 1 or x.shape != y.shape:
        raise ValueError("x and y must be equal-length one-dimensional arrays")
    faces = np.asarray(triangles, dtype=np.int32)
    if faces.ndim != 2 or faces.shape[1] != 3:
        raise ValueError("triangles must have shape (n, 3)")
    if faces.size and (faces.min() < 0 or faces.max() >= x.size):
        raise ValueError("triangle index outside vertex array")
    return x, y, faces


def _triangles(ax, x, y, z, faces, values, association, style):
    data = coordinate_mesh(x, y, z)
    data.SetPolys(cells(faces))
    if values is None and all(key not in style for key in ("color", "facecolor", "cmap")):
        style["color"] = ax._get_lines.get_next_color()
    return Graphic(ax, data, values, association=association, **style)
