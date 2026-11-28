"""NumPy ↔ VTK conventions shared by chart and volume functions."""
import numpy as np
import vtk
from vtk.util.numpy_support import numpy_to_vtk, vtk_to_numpy


def numeric(value):
    if np.ma.isMaskedArray(value):
        return np.ma.asarray(value, dtype=float).filled(np.nan)
    return np.asarray(value, dtype=float)


def array(value, name):
    value = np.ascontiguousarray(value)
    result = numpy_to_vtk(value, deep=True)
    result.SetName(name)
    return result


def points(xyz):
    xyz = np.asarray(xyz, dtype=float)
    if xyz.ndim != 2 or xyz.shape[1] != 3:
        raise ValueError("vertices must have shape (n, 3)")
    p = vtk.vtkPoints()
    p.SetData(array(xyz, "coordinates"))
    return p


def cells(indices, offsets=None):
    indices = np.asarray(indices)
    if offsets is None and indices.ndim != 2:
        raise ValueError("connectivity must be a matrix")
    dtype = np.int32 if indices.dtype == np.int32 and indices.size <= np.iinfo(np.int32).max else np.int64
    connectivity = numpy_to_vtk(np.ascontiguousarray(indices, dtype=dtype).ravel(), deep=True)
    c = vtk.vtkCellArray()
    if offsets is None:
        cell_size = indices.shape[1]
        if cell_size:
            c.SetData(cell_size, connectivity)
            return c
        offsets = np.zeros(len(indices) + 1, dtype=dtype)
    c.SetData(numpy_to_vtk(np.ascontiguousarray(offsets, dtype=dtype), deep=True), connectivity)
    return c


def coordinate_mesh(x, y, z):
    coordinates = vtk.vtkDoubleArray()
    coordinates.SetName("coordinates")
    coordinates.SetNumberOfComponents(3)
    coordinates.SetNumberOfTuples(x.size)
    xyz = vtk_to_numpy(coordinates).reshape(x.shape + (3,))
    xyz[..., 0], xyz[..., 1], xyz[..., 2] = x, y, z
    data = vtk.vtkPolyData()
    grid_points = vtk.vtkPoints()
    grid_points.SetData(coordinates)
    data.SetPoints(grid_points)
    return data


def sequential_ids(count):
    dtype = np.int32 if count <= np.iinfo(np.int32).max else np.int64
    return np.arange(count, dtype=dtype)


def line_data(x, y, z):
    valid = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    if valid.all() and x.size >= 2:
        data = coordinate_mesh(x, y, z)
        data.SetLines(cells(sequential_ids(x.size).reshape(1, -1)))
        return data

    edges = np.flatnonzero(np.diff(valid, prepend=False, append=False)).reshape(-1, 2)
    sizes = edges[:, 1] - edges[:, 0]
    valid[edges[sizes == 1, 0]] = False
    data = coordinate_mesh(x[valid], y[valid], z[valid])
    offsets = np.cumsum(sizes[sizes >= 2])
    data.SetLines(cells(sequential_ids(np.count_nonzero(valid)), np.r_[0, offsets]))
    return data


def vertices(data):
    return vtk_to_numpy(data.GetPoints().GetData()) if data.GetPoints() else np.empty((0, 3))


def output(algorithm, data=None):
    if data is not None:
        algorithm.SetInputData(data)
    algorithm.Update()
    return algorithm.GetOutput()


def surface_arrays(x, y, z):
    x, y, z = map(numeric, (x, y, z))
    if z.ndim != 2:
        raise ValueError("z must be a two-dimensional grid")
    if x.ndim == y.ndim == 1:
        x, y = x[None, :], y[:, None]
    x, y, z = np.broadcast_arrays(x, y, z)
    if z.ndim != 2 or min(z.shape) < 2:
        raise ValueError("surface needs at least two rows and columns")
    return x, y, z


def surface_cells(shape, valid=None):
    ny, nx = shape
    # Both point IDs and offsets must fit in the selected storage width.
    fits_int32 = max(nx * ny, 4 * (ny - 1) * (nx - 1)) <= np.iinfo(np.int32).max
    dtype = np.int32 if fits_int32 else np.int64
    rows = np.arange(ny - 1, dtype=dtype) * nx
    columns = np.arange(nx - 1, dtype=dtype)
    starts = rows[:, None] + columns[None, :]
    if valid is not None:
        valid = valid.reshape(shape)
        starts = starts[valid[:-1, :-1] & valid[:-1, 1:] & valid[1:, 1:] & valid[1:, :-1]]
    # Fill the final connectivity buffer directly in VTK-owned memory.
    connectivity = vtk.vtkTypeInt32Array() if fits_int32 else vtk.vtkTypeInt64Array()
    connectivity.SetNumberOfValues(4 * starts.size)
    quads = vtk_to_numpy(connectivity).reshape(-1, 4)
    starts = starts.ravel()
    quads[:, 0] = starts
    np.add(starts, 1, out=quads[:, 1])
    np.add(starts, nx + 1, out=quads[:, 2])
    np.add(starts, nx, out=quads[:, 3])
    faces = vtk.vtkCellArray()
    faces.SetData(4, connectivity)
    return faces


def volume_arrays(values, coordinates=None):
    v = numeric(values)
    if v.ndim != 3 or min(v.shape) < 2:
        raise ValueError("volume must be a 3-D array with at least two samples per axis")
    shape = (v.shape[1], v.shape[0], v.shape[2])
    if coordinates is None:
        return tuple(np.arange(n, dtype=float) for n in shape), v
    coords = tuple(map(numeric, coordinates))
    if len(coords) != 3:
        raise ValueError("coordinates must contain x, y and z")
    if all(c.ndim == 1 for c in coords):
        if tuple(map(len, coords)) != shape:
            raise ValueError("coordinate lengths must match (nx, ny, nz)")
    elif any(c.shape != v.shape for c in coords):
        raise ValueError("full coordinate grids must match volume shape")
    return coords, v


def volume_array(values, name):
    # Cartesian meshgrid dimensions: (y, x, z). VTK point IDs vary fastest in x.
    ordered = values.transpose(2, 0, 1)
    data = vtk.vtkDoubleArray()
    data.SetName(name)
    data.SetNumberOfValues(values.size)
    vtk_to_numpy(data).reshape(ordered.shape)[...] = ordered
    return data


def volume_grid(coords, values):
    ny, nx, nz = values.shape
    vectors = all(c.ndim == 1 for c in coords)
    if not vectors:
        candidate = (coords[0][0, :, 0], coords[1][:, 0, 0], coords[2][0, 0, :])
        if all(np.array_equal(a, np.broadcast_to(b, values.shape))
               for a, b in zip(coords, np.meshgrid(*candidate, sparse=True))):
            coords, vectors = candidate, True
    spacing = [c[1] - c[0] for c in coords] if vectors else []
    if vectors and all(d > 0 and np.allclose(np.diff(c), d, rtol=1e-10, atol=0)
                       for c, d in zip(coords, spacing)):
        data = vtk.vtkImageData()
        data.SetOrigin(*(c[0] for c in coords))
        data.SetSpacing(*spacing)
    elif vectors:
        data = vtk.vtkRectilinearGrid()
        for setter, c in zip((data.SetXCoordinates, data.SetYCoordinates, data.SetZCoordinates), coords):
            setter(array(c, "coordinate"))
    else:
        data = vtk.vtkStructuredGrid()
        mesh = coordinate_mesh(*(c.transpose(2, 0, 1) for c in coords))
        data.SetPoints(mesh.GetPoints())
    data.SetDimensions(nx, ny, nz)
    data.GetPointData().SetScalars(volume_array(values, "values"))
    return data


def iso_filter(data, level):
    if data.IsA("vtkImageData"):
        contour = vtk.vtkFlyingEdges3D()
        contour.InterpolateAttributesOn()
    else:
        contour = vtk.vtkContourFilter()
    contour.SetValue(0, float(level))
    return output(contour, data)
