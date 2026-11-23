"""Volume filters. Arrays use (y, x, z), including non-cubic volumes."""
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy

from ._geometry import (array, iso_filter, levels as make_levels, numeric,
                        output, poly, sample, surface_mesh, vertices, volume_arrays,
                        volume_flat, volume_grid)
from .scene import Graphic, chart


def _value_args(args, level):
    if len(args) in (2, 5):
        args, level = args[:-1], args[-1]
    coords, v = volume_arrays(args)
    level = (np.nanmin(v) + np.nanmax(v))/2 if level is None else float(level)
    return coords, v, level


@chart
def isosurface(*args, level=None, colors=None, ax, **kwargs):
    """Extract and draw a level surface. The returned handle exposes its polydata."""
    data, c = _isosurface_data(args, level, colors)
    opts = {"lighting": "gouraud", **kwargs}
    if c is None:
        opts.setdefault("color", "C0")
    return Graphic(ax, data, c, **opts)


def _isosurface_data(args, level, colors):
    flags = set()
    while args and isinstance(args[-1], str):
        args, option = args[:-1], args[-1]
        if option not in ("noshare", "verbose"):
            raise ValueError(f"unknown isosurface option {option!r}")
        flags.add(option)
    if len(args) in (3, 6) or (len(args) in (2,5) and np.ndim(args[-1]) == 3):
        args, colors = args[:-1], args[-1]
    coords, v, level = _value_args(args, level)
    grid = volume_grid(coords, v, image=True)
    if colors is not None:
        if np.shape(colors) != v.shape:
            raise ValueError("color volume must match the scalar volume")
        grid.GetPointData().AddArray(array(volume_flat(colors), "colors"))
    data = iso_filter(grid, [level])
    if "noshare" in flags:
        ids = vtk_to_numpy(data.GetPolys().GetConnectivityArray())
        expanded = poly(vertices(data)[ids], np.arange(len(ids)).reshape(-1,3))
        pd = data.GetPointData()
        for i in range(pd.GetNumberOfArrays()):
            attr = pd.GetArray(i)
            expanded.GetPointData().AddArray(array(vtk_to_numpy(attr)[ids], attr.GetName()))
        if pd.GetNormals():
            expanded.GetPointData().SetActiveNormals(pd.GetNormals().GetName())
        data = expanded
    if "verbose" in flags:
        print(f"isosurface: {data.GetNumberOfPoints()} vertices, {data.GetNumberOfPolys()} faces")
    color_array = data.GetPointData().GetArray("colors")
    return data, None if color_array is None else vtk_to_numpy(color_array)


def isosurface_geometry(*args, level=None, colors=None):
    """Return zero-based faces, vertices and optional colors without drawing."""
    data, c = _isosurface_data(args, level, colors)
    result = _face_dict(data)
    if c is not None:
        result["facevertexcdata"] = c.copy()
    return result


@chart
def fimplicit3(func, bounds=(-5, 5), *, samples=51, ax, **kwargs):
    bounds = np.tile(bounds, 3) if len(bounds) == 2 else bounds
    if len(bounds) != 6:
        raise ValueError("bounds must have two or six elements")
    axes = [np.linspace(lo, hi, samples) for lo, hi in np.reshape(bounds, (3, 2))]
    x, y, z = np.meshgrid(*axes)
    return isosurface(ax, *axes, np.broadcast_to(func(x, y, z), x.shape), 0, **kwargs)


@chart
def isocaps(*args, level=None, enclose="above", whichplane="all", ax, **kwargs):
    while args and isinstance(args[-1], str):
        args, option = args[:-1], args[-1]
        if option in ("above", "below"):
            enclose = option
        else:
            whichplane = option
    coords, v, level = _value_args(args, level)
    grids = np.meshgrid(*coords) if coords[0].ndim == 1 else coords
    pieces = []
    for label, dim in zip("xyz", (1, 0, 2)):
        for idx, suffix in ((0, "min"), (-1, "max")):
            if whichplane not in ("all", label+suffix):
                continue
            cut = [np.take(a, idx, axis=dim) for a in grids]
            xyz, faces = surface_mesh(*cut)
            data = poly(xyz, faces)
            data.GetPointData().SetScalars(array(np.take(v, idx, axis=dim).ravel(), "values"))
            clip = vtk.vtkClipPolyData()
            clip.SetValue(level)
            clip.SetInsideOut(enclose == "below")
            pieces.append(output(clip, data))
    if not pieces or enclose not in ("above", "below"):
        raise ValueError("invalid cap plane or enclosure")
    append = vtk.vtkAppendPolyData()
    for piece in pieces:
        append.AddInputData(piece)
    return Graphic(ax, output(append), **kwargs)


def _slice_data(args, method):
    coords, v = volume_arrays(args[:-3])
    grid = volume_grid(coords, v)
    cuts = args[-3:]
    if all(np.ndim(a) == 2 for a in cuts):
        xyz, faces = surface_mesh(*np.broadcast_arrays(*map(numeric, cuts)))
        piece = poly(xyz, faces)
        if method == "linear":
            piece = sample(grid, piece)
            pd = piece.GetPointData()
            scalars = vtk_to_numpy(pd.GetScalars()).copy()
            scalars[vtk_to_numpy(pd.GetArray("vtkValidPointMask")) == 0] = np.nan
            pd.SetScalars(array(scalars, "values"))
        else:
            piece.GetPointData().SetScalars(array(_sample_rectilinear(coords,v,xyz,method), "values"))
        return [piece]
    result = []
    for i, locations in enumerate(cuts):
        for coordinate in np.asarray(locations).ravel():
            plane = vtk.vtkPlane()
            origin = np.zeros(3)
            origin[i] = coordinate
            plane.SetOrigin(origin)
            plane.SetNormal(np.eye(3)[i])
            cutter = vtk.vtkCutter()
            cutter.SetCutFunction(plane)
            piece = output(cutter, grid)
            if method != "linear":
                piece.GetPointData().SetScalars(array(_sample_rectilinear(coords,v,vertices(piece),method), "values"))
            result.append(piece)
    return result


@chart
def slice(*args, method="linear", ax, **kwargs):
    """Cut V or X,Y,Z,V at x/y/z positions (empty lists skip a direction)."""
    if args and isinstance(args[-1], str):
        args, method = args[:-1], args[-1]
    if method not in ("linear", "nearest", "cubic"):
        raise ValueError("slice method must be linear, nearest, or cubic")
    opts = _volume_colors(args[-4], kwargs, ax.color_limits)
    return [Graphic(ax, data, **opts) for data in _slice_data(args, method)]


@chart
def contourslice(*args, levels=10, ax, **kwargs):
    if len(args) in (5, 8):
        args, levels = args[:-1], args[-1]
    spec = make_levels(args[-4], levels)
    opts = _volume_colors(args[-4], kwargs, ax.color_limits)
    return [Graphic(ax, iso_filter(data, spec), **opts) for data in _slice_data(args, "linear")]


def _volume_colors(values, options, limits):
    if any(k in options for k in ("norm","clim","vmin","vmax","cdatamapping")):
        return options
    if limits is not None:
        return {"clim":limits,**options}
    finite = numeric(values)
    if not np.isfinite(finite).any():
        return options
    return {"clim":(np.nanmin(finite), np.nanmax(finite)), **options}


def _sample_at(source, target, name):
    xyz = target.vertices if isinstance(target, Graphic) else numeric(target)
    pd = sample(source, poly(xyz)).GetPointData()
    result = vtk_to_numpy(pd.GetArray(name)).astype(float, copy=True)
    result[vtk_to_numpy(pd.GetArray("vtkValidPointMask")) == 0] = np.nan
    return result


def isocolors(*args):
    target = args[-1]
    rgb = len(args) in (4, 7)
    components = args[-4:-1] if rgb else args[-2:-1]
    coord_args = args[:-4] if rgb else args[:-2]
    values = [_sample_at(volume_grid(*volume_arrays((*coord_args, c))), target, "values") for c in components]
    values = np.column_stack(values) if rgb else values[0]
    if isinstance(target, Graphic):
        target.constant_color = None
        target.set_cdata(values)
    return values


def isonormals(*args, negate=False):
    if isinstance(args[-1], str) and args[-1] == "negate":
        args, negate = args[:-1], True
    target = args[-1]
    source = volume_grid(*volume_arrays(args[:-1]))
    grad = vtk.vtkGradientFilter()
    grad.SetInputScalars(vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS, "values")
    grad.SetResultArrayName("gradient")
    n = _sample_at(output(grad, source), target, "gradient")
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-30)
    if not negate:
        n *= -1
    if isinstance(target, Graphic):
        target.data.GetPointData().SetNormals(array(n, "normals"))
        target.axes.stale = True
    return n


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


def reducevolume(*args):
    coords, v = volume_arrays(args[:-1])
    step = np.broadcast_to(np.asarray(args[-1]), (3,))
    if np.any(step < 1) or np.any(step != step.astype(int)):
        raise ValueError("reduction factors must be positive integers")
    sx, sy, sz = step.astype(int)
    mask = np.s_[::sy, ::sx, ::sz]
    grid = np.meshgrid(*coords) if coords[0].ndim == 1 else coords
    return tuple(a[mask] for a in (*grid, v))


def subvolume(*args):
    coords, v = volume_arrays(args[:-1])
    limits = np.asarray(args[-1], dtype=float).reshape(3, 2)
    selected = []
    for a, (lo, hi) in zip(_rect_axes(coords), limits):
        selected.append(np.where((a >= (-np.inf if np.isnan(lo) else lo)) &
                                 (a <= (np.inf if np.isnan(hi) else hi)))[0])
    ix, iy, iz = selected
    mask = np.ix_(iy, ix, iz)
    grids = np.meshgrid(*coords) if coords[0].ndim == 1 else coords
    return tuple(a[mask] for a in (*grids, v))


def volumebounds(*args):
    if len(args) in (3,6):
        coords, _ = volume_arrays((*args[:-3], args[-3]))
        return np.array([(a.min(), a.max()) for a in coords]).ravel().tolist()
    coords, v = volume_arrays(args)
    return np.array([(a.min(), a.max()) for a in coords]).ravel().tolist() + [np.nanmin(v), np.nanmax(v)]


def flow(*args, grid=False):
    """Generate a 3-D scalar flow example for slice and isosurface plots."""
    if len(args) in (0,1):
        n = int(args[0]) if args else 25
        if n < 2:
            raise ValueError("flow requires at least two samples per axis")
        x,y,z = np.meshgrid(np.linspace(0,10,2*n),np.linspace(-3,3,n),np.linspace(-3,3,n))
    elif len(args) == 3:
        x,y,z = np.broadcast_arrays(*map(numeric,args))
    else:
        raise TypeError("expected zero arguments, N, or X,Y,Z")
    radial = (y-.38*np.sin(.8*x))**2+(z-.38*np.cos(.8*x))**2
    width = .45 + .09*x
    v = 10*np.exp(-radial/width**2) + 2*np.cos(.62*x)*np.exp(-.4*(y*y+z*z))
    return (x,y,z,v) if grid else v


def smooth3(v, method="box", size=3, sigma=.65):
    v = numeric(v)
    sizes = np.broadcast_to(size, (3,))
    if method not in ("box", "gaussian") or sigma <= 0:
        raise ValueError("expected box or gaussian and a positive sigma")
    result = v
    for dim, k in enumerate(sizes):
        if k < 1 or int(k) != k or not int(k) % 2:
            raise ValueError("kernel extents must be positive odd integers")
        k = int(k)
        offset = np.arange(k) - k//2
        w = np.exp(-.5*(offset/sigma)**2) if method == "gaussian" else np.ones(k)
        pads = [(0, 0)]*3
        pads[dim] = (k//2, k//2)
        windows = np.lib.stride_tricks.sliding_window_view(np.pad(result, pads, mode="edge"), k, axis=dim)
        result = windows @ (w/w.sum())
    return result


def _patch_data(args):
    if len(args) == 2:
        return poly(args[1], args[0])
    obj, = args
    if isinstance(obj, Graphic):
        return obj.data
    return poly(obj["vertices"], obj["faces"])


def _face_dict(data):
    triangles = output(vtk.vtkTriangleFilter(), data)
    return {"vertices": vertices(triangles).copy(),
            "faces": vtk_to_numpy(triangles.GetPolys().GetConnectivityArray()).reshape(-1, 3).copy()}


def reducepatch(*args, reduction=.5):
    if np.isscalar(args[-1]):
        args, reduction = args[:-1], float(args[-1])
    triangles = output(vtk.vtkTriangleFilter(), _patch_data(args))
    count = triangles.GetNumberOfPolys()
    keep = reduction/count if reduction > 1 and count else reduction
    if not 0 < keep <= 1:
        raise ValueError("specify a positive keep fraction or target face count")
    decimate = vtk.vtkQuadricDecimation()
    decimate.SetTargetReduction(1-keep)
    return _face_dict(output(decimate, triangles))


def shrinkfaces(*args, factor=.3):
    if np.isscalar(args[-1]):
        args, factor = args[:-1], args[-1]
    f = vtk.vtkShrinkPolyData()
    f.SetShrinkFactor(float(factor)**.5)
    return _face_dict(output(f, _patch_data(args)))
