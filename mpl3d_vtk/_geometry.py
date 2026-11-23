"""NumPy ↔ VTK conventions shared by chart and volume functions."""
import numpy as np
import vtk
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray, vtk_to_numpy


def numeric(value):
    return np.ma.asarray(value, dtype=float).filled(np.nan)


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
    if offsets is None:
        if indices.ndim != 2:
            raise ValueError("connectivity must be a matrix")
        offsets = np.arange(len(indices) + 1, dtype=np.int64) * indices.shape[1]
    idtype = np.int64 if vtk.vtkIdTypeArray().GetDataTypeSize() == 8 else np.int32
    def ids(a):
        return numpy_to_vtkIdTypeArray(np.ascontiguousarray(a, dtype=idtype).ravel(), deep=True)
    c = vtk.vtkCellArray()
    c.SetData(ids(offsets), ids(indices))
    return c


def poly(xyz, faces=None):
    data = vtk.vtkPolyData()
    data.SetPoints(points(xyz))
    if faces is not None:
        try:
            indices = np.asarray(faces)
        except ValueError:
            indices = None
        integer = indices is not None and np.issubdtype(indices.dtype,np.integer)
        if indices is not None and indices.ndim == 2 and (integer or np.isfinite(indices).all()):
            offsets = None
            if indices.shape[1] < 3 and len(indices):
                raise ValueError("polygon faces need at least three vertices")
        else:
            rows = [np.asarray(row,dtype=float) for row in faces]
            rows = [row[~np.isnan(row)] for row in rows]
            if any(len(row) < 3 for row in rows):
                raise ValueError("polygon faces need at least three vertices")
            indices = np.concatenate(rows) if rows else np.empty(0)
            offsets = np.cumsum([0]+[len(row) for row in rows])
            integer = False
        if not integer and (not np.isfinite(indices).all() or not np.equal(indices, np.floor(indices)).all()):
            raise ValueError("face indices must be integers")
        if indices.size and (indices.min() < 0 or indices.max() >= len(xyz)):
            raise ValueError("face index outside vertex array")
        data.SetPolys(cells(indices, offsets))
    return data


def line_data(paths):
    chunks = []
    for path in paths:
        path = numeric(path).reshape(-1, 3)
        valid = np.isfinite(path).all(axis=1)
        edges = np.flatnonzero(np.diff(valid, prepend=False, append=False))
        chunks.extend(path[a:b] for a, b in edges.reshape(-1, 2) if b - a >= 2)
    xyz = np.concatenate(chunks) if chunks else np.empty((0, 3))
    data = poly(xyz)
    offsets = np.cumsum([0] + [len(chunk) for chunk in chunks])
    data.SetLines(cells(np.arange(len(xyz)), offsets))
    return data


def vertices(data):
    return vtk_to_numpy(data.GetPoints().GetData()) if data.GetPoints() else np.empty((0, 3))


def output(algorithm, data=None):
    if data is not None:
        algorithm.SetInputData(data)
    algorithm.Update()
    return algorithm.GetOutput()


def surface_arrays(args):
    if len(args) in (1, 2):
        z = numeric(args[0])
        if z.ndim != 2:
            raise ValueError("Z must be a 2-D matrix")
        y, x = np.indices(z.shape) + 1
        c = args[1] if len(args) == 2 else z
    elif len(args) in (3, 4):
        x, y, z = map(numeric, args[:3])
        if x.ndim == y.ndim == 1:
            x, y = np.meshgrid(x, y)
        x, y, z = np.broadcast_arrays(x, y, z)
        c = args[3] if len(args) == 4 else z
    else:
        raise TypeError("expected Z[, C] or X, Y, Z[, C]")
    if z.ndim != 2 or min(z.shape) < 2:
        raise ValueError("surface needs at least two rows and columns")
    c = np.asanyarray(c)
    if c.dtype != np.uint8 or c.ndim == 2:
        c = numeric(c)
    if c.shape not in (z.shape, z.shape + (3,), z.shape + (4,)):
        raise ValueError("C must match Z or contain RGB(A) values per vertex")
    return x, y, z, c


def surface_mesh(x, y, z):
    xyz = np.column_stack([a.ravel() for a in (x, y, z)])
    idx = np.arange(z.size).reshape(z.shape)[:-1, :-1].ravel()
    nx = z.shape[1]
    faces = idx[:, None] + np.array([0, 1, nx + 1, nx])
    finite = np.isfinite(xyz).all(axis=1)
    if not finite.all():
        faces = faces[finite[faces].all(axis=1)]
    return xyz, faces


def volume_arrays(args):
    if len(args) == 1:
        v = numeric(args[0])
        if v.ndim != 3:
            raise ValueError("volume must have shape (ny, nx, nz)")
        ny, nx, nz = v.shape
        coords = [np.arange(1, n + 1, dtype=float) for n in (nx, ny, nz)]
    elif len(args) == 4:
        *coords, v = map(numeric, args)
    else:
        raise TypeError("expected V or X, Y, Z, V")
    if v.ndim != 3 or min(v.shape) < 2:
        raise ValueError("volume must be a 3-D array with at least two samples per axis")
    shape = (v.shape[1], v.shape[0], v.shape[2])
    if all(c.ndim == 1 for c in coords):
        if tuple(map(len, coords)) != shape:
            raise ValueError("coordinate lengths must match (nx, ny, nz)")
    elif any(c.shape != v.shape for c in coords):
        raise ValueError("full coordinate grids must match volume shape")
    return coords, v


def volume_flat(a):
    # Cartesian meshgrid dimensions: (y, x, z). VTK point IDs vary fastest in x.
    return np.asarray(a).transpose(2, 0, 1).ravel()


def volume_grid(coords, v, *, image=False):
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
