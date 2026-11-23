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
    dtype = np.int32 if indices.dtype == np.int32 and indices.size <= np.iinfo(np.int32).max else np.int64
    if offsets is None:
        if indices.ndim != 2:
            raise ValueError("connectivity must be a matrix")
        offsets = np.arange(len(indices) + 1, dtype=dtype) * indices.shape[1]
    c = vtk.vtkCellArray()
    c.SetData(numpy_to_vtk(np.ascontiguousarray(offsets, dtype=dtype), deep=True),
              numpy_to_vtk(np.ascontiguousarray(indices, dtype=dtype).ravel(), deep=True))
    return c


def poly(xyz, faces=None):
    data = vtk.vtkPolyData()
    data.SetPoints(points(xyz))
    if faces is not None:
        try:
            indices = np.asarray(faces)
        except ValueError:
            indices = None
        if indices is not None and indices.ndim == 2:
            offsets = None
            if indices.shape[1] < 3 and len(indices):
                raise ValueError("polygon faces need at least three vertices")
        else:
            rows = [np.asarray(row) for row in faces]
            if any(row.ndim != 1 or len(row) < 3 for row in rows):
                raise ValueError("polygon faces need at least three vertices")
            indices = np.concatenate(rows) if rows else np.empty(0, dtype=int)
            offsets = np.cumsum([0] + [len(row) for row in rows])
        if indices.size and not np.issubdtype(indices.dtype, np.integer):
            raise ValueError("face indices must be integers")
        if indices.size and (indices.min() < 0 or indices.max() >= len(xyz)):
            raise ValueError("face index outside vertex array")
        data.SetPolys(cells(indices, offsets))
    return data


def line_data(paths):
    if isinstance(paths, np.ndarray) and paths.ndim == 3 and paths.shape[1] >= 2 and paths.shape[2] == 3:
        paths = numeric(paths)
        finite = np.isfinite(paths)
        all_finite = finite.all()
        if all_finite or paths.shape[1] == 2:
            if not all_finite:
                paths = paths[finite.all(axis=(1, 2))]
            xyz = paths.reshape(-1, 3)
            offsets = np.arange(len(paths) + 1) * paths.shape[1]
            return _polyline_data(xyz, offsets)

    chunks = []
    for path in paths:
        path = numeric(path)
        if path.ndim != 2 or path.shape[1] != 3:
            raise ValueError("paths must have shape (n, 3)")
        valid = np.isfinite(path).all(axis=1)
        if valid.all():
            if len(path) >= 2:
                chunks.append(path)
            continue
        edges = np.flatnonzero(np.diff(valid, prepend=False, append=False))
        chunks.extend(path[a:b] for a, b in edges.reshape(-1, 2) if b - a >= 2)
    if len(chunks) == 1:
        xyz = chunks[0]
    else:
        xyz = np.concatenate(chunks) if chunks else np.empty((0, 3))
    return _polyline_data(xyz, np.cumsum([0] + [len(chunk) for chunk in chunks]))


def _polyline_data(xyz, offsets):
    data = poly(xyz)
    dtype = np.int32 if len(xyz) <= np.iinfo(np.int32).max else np.int64
    data.SetLines(cells(np.arange(len(xyz), dtype=dtype), offsets))
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


def surface_faces(shape, valid=None):
    ny, nx = shape
    dtype = np.int32 if nx * ny <= np.iinfo(np.int32).max else np.int64
    rows = np.arange(ny - 1, dtype=dtype) * nx
    columns = np.arange(nx - 1, dtype=dtype)
    starts = rows[:, None] + columns[None, :]
    if valid is not None:
        valid = valid.reshape(shape)
        starts = starts[valid[:-1, :-1] & valid[:-1, 1:] & valid[1:, 1:] & valid[1:, :-1]]
    return starts.reshape(-1, 1) + np.array([0, 1, nx + 1, nx], dtype=dtype)


def surface_poly(x, y, z):
    coordinates = vtk.vtkDoubleArray()
    coordinates.SetName("coordinates")
    coordinates.SetNumberOfComponents(3)
    coordinates.SetNumberOfTuples(z.size)
    xyz = vtk_to_numpy(coordinates).reshape(z.shape + (3,))
    xyz[..., 0], xyz[..., 1], xyz[..., 2] = x, y, z
    grid_points = vtk.vtkPoints()
    grid_points.SetData(coordinates)
    data = vtk.vtkPolyData()
    data.SetPoints(grid_points)
    valid = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    data.SetPolys(cells(surface_faces(z.shape, None if valid.all() else valid)))
    return data


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


def volume_flat(a):
    # Cartesian meshgrid dimensions: (y, x, z). VTK point IDs vary fastest in x.
    return np.asarray(a).transpose(2, 0, 1).ravel()


def volume_grid(coords, v, *, image=False, scalars=True):
    ny, nx, nz = v.shape
    vectors = all(c.ndim == 1 for c in coords)
    if not vectors and image:
        candidate = (coords[0][0,:,0], coords[1][:,0,0], coords[2][0,0,:])
        if all(np.array_equal(a, np.broadcast_to(b, v.shape))
               for a,b in zip(coords, np.meshgrid(*candidate, sparse=True))):
            coords, vectors = candidate, True
    spacing = [c[1]-c[0] for c in coords] if vectors else []
    if image and vectors and all(d > 0 and np.allclose(np.diff(c), d, rtol=1e-10, atol=0)
                                 for c,d in zip(coords, spacing)):
        data = vtk.vtkImageData()
        data.SetOrigin(*(c[0] for c in coords))
        data.SetSpacing(*spacing)
    elif vectors:
        data = vtk.vtkRectilinearGrid()
        for setter, c in zip((data.SetXCoordinates, data.SetYCoordinates, data.SetZCoordinates), coords):
            setter(array(c, "coordinate"))
    else:
        data = vtk.vtkStructuredGrid()
        data.SetPoints(points(np.column_stack([volume_flat(c) for c in coords])))
    data.SetDimensions(nx, ny, nz)
    if scalars:
        data.GetPointData().SetScalars(array(volume_flat(v), "values"))
    return data


def iso_filter(data, values):
    if data.IsA("vtkImageData"):
        f = vtk.vtkFlyingEdges3D()
        f.InterpolateAttributesOn()
    else:
        f = vtk.vtkContourFilter()
    for i, level in enumerate(np.atleast_1d(values)):
        f.SetValue(i, float(level))
    return output(f, data)


def sample(source, target):
    probe = vtk.vtkProbeFilter()
    probe.SetSourceData(source)
    return output(probe, target)


def levels(values, spec):
    if np.ndim(spec) == 0:
        count = int(spec)
        if count < 1 or count != spec:
            raise ValueError("level count must be a positive integer")
        return np.linspace(np.nanmin(values), np.nanmax(values), count + 2)[1:-1]
    return np.asarray(spec, dtype=float).ravel()
