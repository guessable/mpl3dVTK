"""Gridded surfaces, polygons, contours and parametric plots."""
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy

from ._geometry import (array, iso_filter, levels as make_levels, numeric, output,
                        poly, surface_arrays, surface_mesh, vertices)
from .scene import Graphic, chart


def _surface(args, ax, options):
    xdata, ydata, zdata, cdata = [options.pop(k, None) for k in ("xdata","ydata","zdata","cdata")]
    if not args and zdata is not None:
        args = (zdata,) if xdata is None and ydata is None else (xdata,ydata,zdata)
    x, y, z, c = surface_arrays(args)
    if cdata is not None:
        x, y, z, c = surface_arrays((x,y,z,cdata))
    xyz, faces = surface_mesh(x, y, z)
    h = Graphic(ax, poly(xyz, faces), c, **options)
    h.grid_shape = z.shape
    h.color_tracks_height = cdata is None and len(args) in (1,3)
    h.update_surface_normals()
    return h


@chart
def surf(*args, ax, **kwargs):
    """Plot Z[, C] or X, Y, Z[, C]. X and Y can be coordinate vectors."""
    return _surface(args, ax, {"facecolor": "flat", "edgecolor": "black", **kwargs})


@chart
def surface(*args, ax, **kwargs):
    return surf(*args, ax=ax, **kwargs)


def _normals(x, y, z):
    xyz = np.stack((x, y, z), axis=-1)
    n = np.cross(np.gradient(xyz, axis=1), np.gradient(xyz, axis=0))
    return n / np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-30)


@chart
def surfl(*args, ax, light=None, coefficients=(.55, .6, .4, 10), **kwargs):
    """Color by reflectance; pass 'light' for scene illumination."""
    dynamic = bool(args and isinstance(args[-1], str) and args[-1] == "light")
    if dynamic:
        args = args[:-1]
    if len(args) in (3, 5) and np.ndim(args[-1]) == 1 and np.size(args[-1]) == 4:
        args, coefficients = args[:-1], args[-1]
    if len(args) in (2, 4) and np.ndim(args[-1]) == 1:
        args, light = args[:-1], args[-1]
    x, y, z, _ = surface_arrays(args)
    direction = np.array(light if light is not None else [-60, 35], dtype=float)
    if direction.size == 2:
        az, el = np.deg2rad(direction)
        direction = np.array([np.sin(az)*np.cos(el), -np.cos(az)*np.cos(el), np.sin(el)])
    if direction.shape != (3,) or np.linalg.norm(direction) == 0:
        raise ValueError("light must be [azimuth,elevation] or a nonzero xyz vector")
    direction /= np.linalg.norm(direction)
    n = _normals(x, y, z)
    ambient, diffuse, specular, exponent = coefficients
    if dynamic:
        lamp = vtk.vtkLight()
        lamp.SetPosition(*direction)
        lamp.SetFocalPoint(0, 0, 0)
        ax.renderer.AddLight(lamp)
        return _surface((x, y, z), ax, {"lighting": "gouraud", **kwargs})
    az, el = np.deg2rad([ax._azimuth, ax._elevation])
    eye = np.array([np.sin(az)*np.cos(el), -np.cos(az)*np.cos(el), np.sin(el)])
    dot = np.maximum(n @ direction, 0)
    reflected = 2*dot[..., None]*n - direction
    c = ambient + diffuse*dot + specular*np.maximum(reflected @ eye, 0)**exponent
    return _surface((x, y, z, c), ax, kwargs)


@chart
def surfnorm(*args, ax, scale=1., **kwargs):
    from .vectors import quiver3
    x, y, z, c = surface_arrays(args)
    h = surf(x, y, z, c, ax=ax, **kwargs)
    n = _normals(x, y, z)
    arrows = quiver3(x, y, z, *np.moveaxis(n, -1, 0), scale, ax=ax)
    return h, arrows


@chart
def mesh(*args, ax, **kwargs):
    ax.renderer.UseHiddenLineRemovalOn()
    return _surface(args, ax, {"representation": "wireframe", "edgecolor":"interp", **kwargs})


@chart
def contour3(*args, ax, levels=10, plane=None, return_matrix=False, **kwargs):
    if args and isinstance(args[-1], str):
        from matplotlib.axes._base import _process_plot_format
        style, _, color = _process_plot_format(args[-1])
        args = args[:-1]
        if color is not None:
            kwargs.setdefault("color", color)
        if style not in (None, "None"):
            kwargs.setdefault("linestyle", style)
    if len(args) in (2, 4):
        args, levels = args[:-1], args[-1]
    x, y, z, _ = surface_arrays(args)
    xyz, faces = surface_mesh(x, y, z)
    data = poly(xyz, faces)
    data.GetPointData().SetScalars(array(z.ravel(), "height"))
    lines = iso_filter(data, make_levels(z, levels))
    if plane is not None and lines.GetNumberOfPoints():
        vertices(lines)[:, 2] = plane
        lines.GetPoints().Modified()
    join = vtk.vtkStripper()
    join.JoinContiguousSegmentsOn()
    lines = output(join, lines)
    handle = Graphic(ax, lines, **kwargs)
    handle.contour_levels = np.unique(make_levels(z,levels))
    if return_matrix:
        from .vectors import _paths
        scalar_array = lines.GetPointData().GetScalars()
        values = vtk_to_numpy(scalar_array) if scalar_array else []
        offsets = vtk_to_numpy(lines.GetLines().GetOffsetsArray())[:-1]
        ids = vtk_to_numpy(lines.GetLines().GetConnectivityArray())
        columns = [np.column_stack(([values[ids[i]], len(path)], path[:,:2].T))
                   for i,path in zip(offsets,_paths(lines))]
        return (np.hstack(columns) if columns else np.empty((2,0))), handle
    return handle


def clabel(*args, levels=None, **kwargs):
    """Add Matplotlib Text3D labels to selected contour line components."""
    from .vectors import _paths
    from .scene import _property_name
    handle = args[-1]
    if not isinstance(handle,Graphic):
        raise TypeError("pass a contour handle, optionally preceded by its contour matrix")
    values = handle.data.GetPointData().GetScalars()
    if values is None:
        return []
    values = vtk_to_numpy(values)
    allowed = getattr(handle,"contour_levels",np.unique(values)) if levels is None else np.atleast_1d(levels)
    opts = {_property_name(k).lower():v for k,v in kwargs.items()}
    starts = vtk_to_numpy(handle.data.GetLines().GetOffsetsArray())[:-1]
    ids = vtk_to_numpy(handle.data.GetLines().GetConnectivityArray())
    labels = []
    for i,path in zip(starts,_paths(handle.data)):
        value = values[ids[i]]
        if not np.isclose(value,allowed).any():
            continue
        midpoint = path[len(path)//2]
        label = handle.axes.text(*midpoint, f"{value:g}",ha="center",va="center",**opts)
        labels.append(label)
    handle.annotations.extend(labels)
    return labels


def _with_contours(fn, args, ax, levels, kwargs):
    x, y, z, c = surface_arrays(args)
    low = np.nanmin(z)
    base = low - .12 * max(np.nanmax(z) - low, 1e-8)
    return fn(x, y, z, c, ax=ax, **kwargs), contour3(x, y, z, levels, ax=ax, plane=base)


@chart
def surfc(*args, ax, levels=10, **kwargs):
    return _with_contours(surf, args, ax, levels, kwargs)


@chart
def meshc(*args, ax, levels=10, **kwargs):
    return _with_contours(mesh, args, ax, levels, kwargs)


@chart
def meshz(*args, ax, base=None, **kwargs):
    x, y, z, c = surface_arrays(args)
    if base is None:
        base = np.nanmin(z) - .1*np.ptp(z[np.isfinite(z)])
    def ring(a):
        return np.concatenate((a[0], a[1:, -1], a[-1, -2::-1], a[-2::-1, 0]))
    rim_x, rim_y, rim_z, rim_c = map(ring, (x, y, z, c))
    curtain = mesh(np.stack((rim_x, rim_x)), np.stack((rim_y, rim_y)),
                   np.stack((rim_z, np.full_like(rim_z, base))), np.stack((rim_c, rim_c)), ax=ax, **kwargs)
    return mesh(x, y, z, c, ax=ax, **kwargs), curtain


@chart
def waterfall(*args, ax, base=None, **kwargs):
    x, y, z, c = surface_arrays(args)
    base = np.nanmin(z) if base is None else base
    from ._geometry import line_data
    xyz = np.stack((x, y, z), axis=-1)
    floor = xyz.copy()
    floor[..., 2] = base
    ids = np.arange(z.size).reshape(z.shape)[:, :-1].ravel()
    faces = np.column_stack((ids, ids+1, ids+1+z.size, ids+z.size))
    all_xyz = np.vstack((xyz.reshape(-1, 3), floor.reshape(-1, 3)))
    faces = faces[np.isfinite(all_xyz[faces]).all(axis=(1, 2))]
    curtain = Graphic(ax, poly(all_xyz, faces), color=ax.get_facecolor())
    lines = line_data(xyz)
    finite = np.isfinite(xyz).all(axis=-1)
    # Each uninterrupted line must have at least two vertices.
    adjacent = np.zeros_like(finite)
    adjacent[:, 1:] |= finite[:, :-1]
    adjacent[:, :-1] |= finite[:, 1:]
    return curtain, Graphic(ax, lines, c[finite & adjacent], **kwargs)


@chart
def ribbon(*args, ax, width=.75, **kwargs):
    if len(args) == 3:
        args, width = args[:2], args[2]
    z = numeric(args[-1])
    if z.ndim == 1:
        z = z[:, None]
    y = np.arange(1, len(z)+1) if len(args) == 1 else numeric(args[0])
    if y.ndim == 1:
        y = np.broadcast_to(y[:, None], z.shape)
    result = []
    for j in range(z.shape[1]):
        x = np.broadcast_to(j+1 + np.array([-width/2, width/2]), (len(z), 2))
        result.append(surf(x, np.repeat(y[:, j:j+1], 2, axis=1),
                           np.repeat(z[:, j:j+1], 2, axis=1), ax=ax, **kwargs))
    return result


def surf2patch(*args, triangles=False):
    if args and isinstance(args[-1], str) and args[-1] == "triangles":
        args, triangles = args[:-1], True
    x, y, z, c = surface_arrays(args)
    xyz, faces = surface_mesh(x, y, z)
    if triangles:
        faces = np.vstack((faces[:, [0, 1, 2]], faces[:, [0, 2, 3]]))
    return dict(vertices=xyz, faces=faces, facevertexcdata=c.reshape((z.size,) + c.shape[2:]))


@chart
def patch(*args, ax, faces=None, vertices=None, facevertexcdata=None, index_base=0, **kwargs):
    if len(args) == 1 and isinstance(args[0], dict):
        return patch(ax, **args[0], **kwargs)
    if len(args) == 1 and isinstance(args[0], Graphic):
        h = args[0]
        return Graphic(ax, h.data, h._values, **kwargs)
    if len(args) >= 3:
        return fill3(ax, *args, **kwargs)
    if len(args) == 2:
        faces, vertices = args
    if index_base not in (0,1):
        raise ValueError("index_base must be 0 or 1")
    if faces is None or vertices is None:
        raise TypeError("patch requires Faces and Vertices")
    f = faces if index_base == 0 else [np.asarray(row)-1 for row in faces]
    data = poly(vertices, f)
    assoc = "point"
    if facevertexcdata is not None and len(facevertexcdata) == len(f) != len(vertices):
        assoc = "cell"
    return Graphic(ax, data, facevertexcdata, association=assoc, **kwargs)


@chart
def fill3(x, y, z, c="C0", *, ax, **kwargs):
    arrays = np.broadcast_arrays(*map(numeric, (x, y, z)))
    xyz = np.column_stack([v.ravel(order="F") for v in arrays])
    n = len(arrays[0])
    rows = np.arange(len(xyz)).reshape(-1,n)
    faces = [row[np.isfinite(xyz[row]).all(axis=1)] for row in rows]
    if isinstance(c, str) or (np.shape(c) == (3,) and np.size(x) != 3):
        return Graphic(ax, poly(xyz, faces), color=c, **kwargs)
    c = np.asarray(c)
    return patch(ax, faces, xyz, facevertexcdata=c.ravel(order="F") if c.shape == arrays[0].shape else c, **kwargs)


def _triangulation(obj):
    for connectivity, points_name in (("ConnectivityList","Points"),("simplices","points")):
        if hasattr(obj,connectivity) and hasattr(obj,points_name):
            return np.asarray(getattr(obj,connectivity)), numeric(getattr(obj,points_name))
    return None


def _tet_faces(t):
    return t[:,[[0,2,1],[0,1,3],[1,2,3],[2,0,3]]].reshape(-1,3)


@chart
def trisurf(tri, x=None, y=None, z=None, c=None, *, index_base=0, ax, **kwargs):
    obj = _triangulation(tri)
    if obj is None:
        if np.ndim(tri) != 2 or np.shape(tri)[1] != 3 or any(a is None for a in (x,y,z)):
            raise ValueError("expected T with shape (n,3) and three coordinate arrays")
        xyz = np.column_stack([numeric(a).ravel() for a in (x,y,z)])
    else:
        tri,xyz = obj
        if xyz.ndim != 2 or xyz.shape[1] != 3 or tri.ndim != 2 or tri.shape[1] not in (3,4):
            raise ValueError("expected a three-dimensional triangulation")
        if tri.shape[1] == 4:
            boundary = _tet_faces(tri)
            _,first,count = np.unique(np.sort(boundary,axis=1),axis=0,return_index=True,return_counts=True)
            tri = boundary[first[count == 1]]
        if c is None:
            c = x
    return patch(ax, tri, xyz, facevertexcdata=xyz[:, 2] if c is None else c,
                 index_base=index_base, **{"edgecolor": "black", **kwargs})


@chart
def trimesh(*args, ax, **kwargs):
    ax.renderer.UseHiddenLineRemovalOn()
    if len(args) == 3:
        args = (*args,np.zeros_like(args[-1]))
    return trisurf(ax, *args, **{"representation": "wireframe", "edgecolor": "interp", **kwargs})


@chart
def tetramesh(t, xyz=None, c=None, *, index_base=0, ax, **kwargs):
    obj = _triangulation(t)
    if obj is not None:
        if c is None:
            c = xyz
        t,xyz = obj
    t = np.asarray(t) - index_base
    if t.ndim != 2 or t.shape[1] != 4:
        raise ValueError("tetrahedra need four indices per row")
    faces = _tet_faces(t)
    values = np.repeat(np.arange(1, len(t)+1) if c is None else c, 4)
    return Graphic(ax, poly(xyz, faces), values, association="cell", **{"edgecolor": "black", **kwargs})


def _function_grid(args, samples):
    funcs = list(args)
    if not funcs or samples < 2 or int(samples) != samples:
        raise ValueError("supply functions and at least two samples per axis")
    samples = int(samples)
    bounds = (-5, 5) if callable(funcs[-1]) else funcs.pop()
    bounds = np.tile(bounds, 2) if len(bounds) == 2 else bounds
    if len(bounds) != 4 or not np.all(np.asarray(bounds)[::2] < np.asarray(bounds)[1::2]):
        raise ValueError("expected [min,max] or [umin,umax,vmin,vmax]")
    u, v = np.meshgrid(np.linspace(*bounds[:2], samples), np.linspace(*bounds[2:], samples))
    if len(funcs) == 1:
        return u, v, np.broadcast_to(funcs[0](u, v), u.shape)
    if len(funcs) != 3:
        raise TypeError("expected f(x,y) or three parametric functions")
    return tuple(np.broadcast_to(f(u, v), u.shape) for f in funcs)


@chart
def fsurf(*args, samples=35, showcontour=False, ax, **kwargs):
    fn = surfc if showcontour in (True, "on") else surf
    return fn(ax, *_function_grid(args, samples), **kwargs)


@chart
def fmesh(*args, samples=35, showcontour=False, ax, **kwargs):
    fn = meshc if showcontour in (True, "on") else mesh
    return fn(ax, *_function_grid(args, samples), **kwargs)


@chart
def pcolor(*args, ax, **kwargs):
    x, y, c, _ = surface_arrays(args)
    plane = np.where(np.isfinite(c),0.,np.nan)
    h = surf(ax, x, y, plane, c, **kwargs)
    ax.set_view(0, 90)
    return h


def peaks(n=49, y=None, *, grid=False):
    if y is None:
        a = np.linspace(-3, 3, n) if np.ndim(n) == 0 else numeric(n)
        x, y = np.meshgrid(a, a)
    else:
        x = numeric(n)
    z = 3*(1-x)**2*np.exp(-x*x-(y+1)**2) - 10*(x/5-x**3-y**5)*np.exp(-x*x-y*y) - np.exp(-(x+1)**2-y*y)/3
    return (x, y, z) if grid else z


def sphere(n=20):
    a, b = np.meshgrid(np.linspace(0, 2*np.pi, n+1), np.linspace(-np.pi/2, np.pi/2, n+1))
    return np.cos(b)*np.cos(a), np.cos(b)*np.sin(a), np.sin(b)


def ellipsoid(xc, yc, zc, xr, yr, zr, n=20):
    x, y, z = sphere(n)
    return xc+xr*x, yc+yr*y, zc+zr*z


def cylinder(r=1, n=20):
    r = np.atleast_1d(numeric(r)).ravel()
    if len(r) == 1:
        r = r.repeat(2)
    a = np.linspace(0, 2*np.pi, n+1)
    return r[:, None]*np.cos(a), r[:, None]*np.sin(a), np.broadcast_to(np.linspace(0, 1, len(r))[:, None], (len(r), n+1))
