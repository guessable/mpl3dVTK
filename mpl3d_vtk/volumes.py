"""VTK geometry filters for scalar fields stored in (y, x, z) order."""
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy

from ._geometry import (array, iso_filter, levels as contour_levels, numeric, output,
                        poly, sample, surface_poly, vertices, volume_arrays, volume_flat, volume_grid)
from .scene import Graphic


def _isosurface_data(values, level, coordinates, color_values, share_vertices):
    coords, values = volume_arrays(values, coordinates)
    if level is None:
        level = (np.nanmin(values) + np.nanmax(values)) / 2
    grid = volume_grid(coords, values, image=True)
    if color_values is not None:
        color_values = numeric(color_values)
        if color_values.shape != values.shape:
            raise ValueError("color_values must match the scalar volume")
        grid.GetPointData().AddArray(array(volume_flat(color_values), "colors"))
    data = iso_filter(grid, [level])
    if not share_vertices:
        ids = vtk_to_numpy(data.GetPolys().GetConnectivityArray())
        expanded = poly(vertices(data)[ids], np.arange(len(ids)).reshape(-1, 3))
        if color_values is not None:
            colors = data.GetPointData().GetArray("colors")
            expanded.GetPointData().AddArray(array(vtk_to_numpy(colors)[ids], "colors"))
        normals = data.GetPointData().GetNormals()
        if normals is not None:
            expanded.GetPointData().SetNormals(array(vtk_to_numpy(normals)[ids], "normals"))
        data = expanded
    colors = data.GetPointData().GetArray("colors")
    return data, None if colors is None else vtk_to_numpy(colors)


def extract_isosurface(values, *, level=None, coordinates=None, color_values=None, share_vertices=True):
    """Return a mesh dictionary with zero-based faces, vertices and optional values."""
    data, colors = _isosurface_data(values, level, coordinates, color_values, share_vertices)
    faces = vtk_to_numpy(data.GetPolys().GetConnectivityArray()).reshape(-1, 3)
    mesh = {"vertices": vertices(data).copy(), "faces": faces.copy()}
    if colors is not None:
        mesh["values"] = colors.copy()
    return mesh


def plot_isosurface(self, values, *, level=None, coordinates=None, color_values=None,
                    share_vertices=True, **style):
    """Extract and draw a surface at a scalar level in a 3-D volume."""
    data, colors = _isosurface_data(values, level, coordinates, color_values, share_vertices)
    if colors is None and all(key not in style for key in ("color", "facecolor", "cmap")):
        style["color"] = self._get_lines.get_next_color()
    style.setdefault("lighting", "gouraud")
    return Graphic(self, data, colors, **style)


def _slice_data(coords, values, locations, sample_surface, interpolation):
    if interpolation not in ("linear", "nearest", "cubic"):
        raise ValueError("interpolation must be 'linear', 'nearest' or 'cubic'")
    grid = volume_grid(coords, values, image=True)
    if sample_surface is not None:
        if any(np.size(cuts) for cuts in locations):
            raise ValueError("use either axis locations or sample_surface")
        x, y, z = np.broadcast_arrays(*map(numeric, sample_surface))
        piece = surface_poly(x, y, z)
        if interpolation == "linear":
            piece = sample(grid, piece)
            pd = piece.GetPointData()
            scalars = vtk_to_numpy(pd.GetScalars()).copy()
            scalars[vtk_to_numpy(pd.GetArray("vtkValidPointMask")) == 0] = np.nan
        else:
            scalars = _sample_rectilinear(coords, values, vertices(piece), interpolation)
        piece.GetPointData().SetScalars(array(scalars, "values"))
        return [piece]

    pieces = []
    for dimension, cuts in enumerate(locations):
        normal = np.eye(3)[dimension]
        plane = vtk.vtkPlane()
        plane.SetNormal(normal)
        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(plane)
        for coordinate in numeric(cuts).ravel():
            if not np.isfinite(coordinate):
                raise ValueError("slice locations must be finite")
            origin = np.zeros(3)
            origin[dimension] = coordinate
            plane.SetOrigin(origin)
            # The cutter reuses its output on Update().
            piece = vtk.vtkPolyData()
            piece.ShallowCopy(output(cutter, grid))
            if interpolation != "linear":
                scalars = _sample_rectilinear(coords, values, vertices(piece), interpolation)
                piece.GetPointData().SetScalars(array(scalars, "values"))
            pieces.append(piece)
    return pieces


def _volume_style(values, style):
    if "norm" not in style:
        if "vmin" not in style:
            style["vmin"] = np.nanmin(values)
        if "vmax" not in style:
            style["vmax"] = np.nanmax(values)
    return style


def plot_volume_slices(self, values, *, coordinates=None, x=(), y=(), z=(),
                       sample_surface=None, interpolation="linear", **style):
    """Draw scalar slices at x, y and z locations or on a supplied coordinate grid."""
    coords, values = volume_arrays(values, coordinates)
    pieces = _slice_data(coords, values, (x, y, z), sample_surface, interpolation)
    style = _volume_style(values, style)
    return [Graphic(self, piece, **style) for piece in pieces]


def plot_slice_contours(self, values, *, coordinates=None, x=(), y=(), z=(),
                        levels=10, **style):
    """Draw contour lines on axis-aligned volume slices."""
    coords, values = volume_arrays(values, coordinates)
    pieces = _slice_data(coords, values, (x, y, z), None, "linear")
    levels = contour_levels(values, levels)
    style = _volume_style(values, style)
    return [Graphic(self, iso_filter(piece, levels), **style) for piece in pieces]


def _rect_axes(coords):
    if coords[0].ndim == 1:
        return coords
    axes = (coords[0][0, :, 0], coords[1][:, 0, 0], coords[2][0, 0, :])
    if not all(np.allclose(a, b) for a, b in zip(coords, np.meshgrid(*axes, sparse=True))):
        raise ValueError("operation requires a rectilinear meshgrid")
    return axes


def _sample_rectilinear(coords, values, xyz, method):
    """Nearest or tensor-product interpolation in (y, x, z) storage order."""
    axes = _rect_axes(coords)
    outside = ~np.isfinite(xyz).all(axis=1)
    indices, weights = [], []
    for axis, x in zip(axes, xyz.T):
        order = np.arange(len(axis)) if axis[0] < axis[-1] else np.arange(len(axis)-1,-1,-1)
        a = axis[order]
        if not np.all(np.diff(a) > 0):
            raise ValueError("interpolation requires strictly monotonic axes")
        outside |= (x < a[0]) | (x > a[-1])
        right = np.clip(np.searchsorted(a,x),1,len(a)-1)
        if method == "nearest":
            near = np.where(x-a[right-1] < a[right]-x, right-1, right)
            indices.append(order[near[:,None]])
            weights.append(np.ones((len(x),1)))
            continue
        count = min(len(a), 4 if method == "cubic" else 2)
        start = np.clip(right-(count//2),0,len(a)-count)
        stencil = start[:,None]+np.arange(count)
        nodes = a[stencil]
        basis = np.ones_like(nodes)
        for j in range(count):
            for k in range(count):
                if j != k:
                    basis[:,j] *= (x-nodes[:,k])/(nodes[:,j]-nodes[:,k])
        indices.append(order[stencil])
        weights.append(basis)
    ix,iy,iz = indices
    wx,wy,wz = weights
    neighborhood = values[iy[:,:,None,None], ix[:,None,:,None], iz[:,None,None,:]]
    result = np.einsum("nijk,ni,nj,nk->n", neighborhood,wy,wx,wz)
    result[outside] = np.nan
    return result
