"""VTK geometry filters for scalar fields stored in (y, x, z) order."""
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy

from ._geometry import (array, cells, iso_filter, numeric, points, sequential_ids, vertices,
                        volume_array, volume_arrays, volume_grid)
from .scene import Graphic


def _isosurface_data(values, level, coordinates, color_values, share_vertices):
    coords, values = volume_arrays(values, coordinates)
    if level is None:
        level = (np.nanmin(values) + np.nanmax(values)) / 2
    grid = volume_grid(coords, values)
    if color_values is not None:
        color_values = numeric(color_values)
        if color_values.shape != values.shape:
            raise ValueError("color_values must match the scalar volume")
        grid.GetPointData().AddArray(volume_array(color_values, "colors"))
    data = iso_filter(grid, level)
    if not share_vertices:
        ids = vtk_to_numpy(data.GetPolys().GetConnectivityArray())
        expanded = data.NewInstance()
        expanded.SetPoints(points(vertices(data)[ids]))
        expanded.SetPolys(cells(sequential_ids(len(ids)).reshape(-1, 3)))
        if color_values is not None:
            colors = data.GetPointData().GetArray("colors")
            expanded.GetPointData().AddArray(array(vtk_to_numpy(colors)[ids], "colors"))
        normals = data.GetPointData().GetNormals()
        if normals is not None:
            expanded.GetPointData().SetNormals(array(vtk_to_numpy(normals)[ids], "normals"))
        data = expanded
    colors = data.GetPointData().GetArray("colors")
    return data, None if colors is None else vtk_to_numpy(colors)


def plot_isosurface(self, values, *, level=None, coordinates=None, color_values=None,
                    share_vertices=True, **style):
    """Extract and draw a surface at a scalar level in a 3-D volume."""
    data, colors = _isosurface_data(values, level, coordinates, color_values, share_vertices)
    if colors is None and all(key not in style for key in ("color", "facecolor", "cmap")):
        style["color"] = self._get_lines.get_next_color()
    style.setdefault("lighting", "gouraud")
    return Graphic(self, data, colors, **style)
