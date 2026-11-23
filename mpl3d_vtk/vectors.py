"""VTK-instanced glyphs, streamline integration and vector field diagnostics."""
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy

from ._geometry import (array, line_data, numeric, output, poly, sample, surface_mesh,
                        vertices, volume_arrays, volume_flat, volume_grid)
from .scene import Graphic, chart
from .volumes import _rect_axes, _sample_rectilinear


def _xyz(values):
    return np.column_stack([a.ravel() for a in np.broadcast_arrays(*map(numeric, values))])


def _glyphs(ax, xyz, vectors, source, scale, kwargs, colors=None):
    valid = np.isfinite(xyz).all(axis=1) & np.isfinite(vectors).all(axis=1)
    xyz, vectors = xyz[valid], vectors[valid]
    speed = np.linalg.norm(vectors, axis=1)
    if scale < 0:
        raise ValueError("scale must be nonnegative")
    factor = 1.
    if scale and len(xyz):
        spans = np.ptp(xyz, axis=0)
        active = spans[spans > 0]
        spacing = (np.prod(active)/len(xyz)) ** (1/max(len(active), 1))
        factor = scale*spacing/max(speed.max(), 1e-30)
    data = poly(xyz)
    data.GetPointData().SetVectors(array(vectors, "vectors"))
    data.GetPointData().AddArray(array(speed, "speed"))
    mapper = vtk.vtkGlyph3DMapper()
    mapper.SetSourceConnection(source.GetOutputPort())
    mapper.SetOrientationArray("vectors")
    mapper.SetScaleArray("speed")
    mapper.SetScaleModeToScaleByMagnitude()
    mapper.SetScaleFactor(factor)
    opts = {"color":"C0",**kwargs} if colors is None and "cmap" not in kwargs else kwargs
    rgba = speed if colors is None else np.asarray(colors)[valid]
    return Graphic(ax, data, rgba, mapper=mapper, **opts)


@chart
def quiver3(*args, scale=.9, autoscale=True, autoscalefactor=None, showarrowhead=True,
            maxheadsize=.2, ax, **kwargs):
    """Arrows at X,Y,Z with components U,V,W. Scale 0 preserves lengths."""
    filled = bool(args and isinstance(args[-1],str) and args[-1] == "filled")
    if filled:
        args = args[:-1]
    if args and isinstance(args[-1],str):
        from matplotlib.axes._base import _process_plot_format
        style, marker, color = _process_plot_format(args[-1])
        args = args[:-1]
        if color is not None:
            kwargs.setdefault("color",color)
        if style not in (None,"None"):
            kwargs.setdefault("linestyle",style)
        if marker not in (None,"None"):
            kwargs.setdefault("marker",marker)
    if len(args) in (5, 7):
        args, scale = args[:-1], args[-1]
    if len(args) == 4:
        z, u, v, w = args
        y, x = np.indices(np.atleast_2d(z).shape)+1
    elif len(args) == 6:
        x, y, z, u, v, w = args
    else:
        raise TypeError("expected Z,U,V,W or X,Y,Z,U,V,W")
    if np.ndim(x) == np.ndim(y) == 1 and np.ndim(z) == 2:
        x, y = np.meshgrid(x, y)
    x, y, z, u, v, w = np.broadcast_arrays(x, y, z, u, v, w)
    marker = kwargs.pop("marker",None)
    marker_size = kwargs.pop("markersize",6)
    source = vtk.vtkArrowSource()
    show_head = showarrowhead not in (False,"off")
    source.SetTipLength(float(maxheadsize) if show_head else 0)
    source.SetTipRadius(.08 if show_head else 0)
    source.SetShaftRadius(.014)
    if autoscalefactor is not None:
        scale = autoscalefactor
    if autoscale in (False,"off"):
        scale = 0
    h = _glyphs(ax, _xyz((x,y,z)), _xyz((u,v,w)), source, scale, kwargs)
    if marker not in (None,"none"):
        from .charts import scatter3
        marker_flags = (marker,"filled") if filled else (marker,)
        h.markers = scatter3(ax,x,y,z,marker_size**2,None,*marker_flags,color=kwargs.get("color","C0"))
    return h


def _field(args):
    coords, u = volume_arrays((*args[:-3], args[-3]))
    u, v, w = map(numeric, args[-3:])
    if not u.shape == v.shape == w.shape:
        raise ValueError("vector components must have identical shapes")
    data = volume_grid(coords, np.sqrt(u*u+v*v+w*w))
    data.GetPointData().SetVectors(array(np.column_stack([volume_flat(a) for a in (u,v,w)]), "vectors"))
    return data


@chart
def coneplot(*args, scale=.9, method="linear", colors=None, quiver=False, ax, **kwargs):
    nointerp = False
    while args and isinstance(args[-1],str):
        args, flag = args[:-1], args[-1]
        if flag == "nointerp":
            nointerp = True
        elif flag == "quiver":
            quiver = True
        elif flag in ("nearest","linear","cubic"):
            method = flag
        else:
            raise ValueError(f"unknown coneplot option {flag!r}")
    if len(args) in (7,10):
        args, option = args[:-1], args[-1]
        if np.ndim(option) == 0:
            scale = option
        else:
            colors = option
    if quiver:
        source = vtk.vtkArrowSource()
    else:
        source = vtk.vtkConeSource()
        source.SetCenter(.5,0,0)
        source.SetDirection(1,0,0)
        source.SetRadius(.22)
        source.SetResolution(16)
    if nointerp:
        if len(args) != 6:
            raise TypeError("nointerp expects X,Y,Z,U,V,W")
        if all(np.ndim(a) == 1 for a in args[:3]) and np.ndim(args[3]) == 3:
            coords = np.meshgrid(*args[:3])
        else:
            coords = args[:3]
        xyz, vec = _xyz(coords), _xyz(args[3:])
        if colors is not None:
            colors = numeric(colors).ravel()
    else:
        if method not in ("linear","nearest","cubic"):
            raise ValueError("unknown coneplot interpolation method")
        xyz = _xyz(args[-3:])
        field = _field(args[:-3])
        if method == "linear":
            if colors is not None:
                field.GetPointData().AddArray(array(volume_flat(colors), "colors"))
            sampled = sample(field,poly(xyz)).GetPointData()
            valid = vtk_to_numpy(sampled.GetArray("vtkValidPointMask")).astype(bool)
            xyz = xyz[valid]
            vec = vtk_to_numpy(sampled.GetArray("vectors"))[valid]
            if colors is not None:
                colors = vtk_to_numpy(sampled.GetArray("colors"))[valid]
        else:
            coords,_ = volume_arrays(args[:-5])
            vec = np.column_stack([_sample_rectilinear(coords,numeric(a),xyz,method) for a in args[-6:-3]])
            if colors is not None:
                colors = _sample_rectilinear(coords,numeric(colors),xyz,method)
    return _glyphs(ax, xyz, vec, source, scale, kwargs, colors)


def _trace(field, seeds, step=.1, max_steps=10000, direction="forward"):
    if step <= 0 or max_steps < 1:
        raise ValueError("step and max_steps must be positive")
    tracer = vtk.vtkStreamTracer()
    tracer.SetSourceData(poly(seeds))
    tracer.SetIntegratorTypeToRungeKutta4()
    tracer.SetInitialIntegrationStep(step)
    tracer.SetMaximumNumberOfSteps(int(max_steps))
    tracer.SetMaximumPropagation(max(field.GetLength(), 1e-10) * 30)
    methods = {"forward": tracer.SetIntegrationDirectionToForward,
               "backward": tracer.SetIntegrationDirectionToBackward,
               "both": tracer.SetIntegrationDirectionToBoth}
    methods[direction]()
    return output(tracer, field)


def _paths(data):
    offsets = vtk_to_numpy(data.GetLines().GetOffsetsArray())
    ids = vtk_to_numpy(data.GetLines().GetConnectivityArray())
    xyz = vertices(data)
    return [xyz[ids[a:b]].copy() for a, b in zip(offsets, offsets[1:])]


def _stream_data(args, **options):
    if len(args) == 1:
        paths = args[0]
        if isinstance(paths, Graphic):
            return paths.data
        if isinstance(paths, np.ndarray) and paths.ndim == 2:
            paths = [paths]
        paths = [numeric(p) for p in paths]
        paths = [np.column_stack((p,np.zeros(len(p)))) if p.ndim == 2 and p.shape[1] == 2 else p for p in paths]
        return line_data(paths)
    if len(args) in (7, 10):
        args, opt = args[:-1], np.atleast_1d(args[-1])
        options.update(step=opt[0])
        if len(opt) > 1:
            options.update(max_steps=int(opt[1]))
    return _trace(_field(args[:-3]), _xyz(args[-3:]), **options)


def stream3(*args, step=.1, max_steps=10000, direction="forward"):
    return _paths(_stream_data(args, step=step, max_steps=max_steps, direction=direction))


def _planar_field(args):
    u,v = [numeric(a) for a in args[-2:]]
    if u.ndim != 2 or u.shape != v.shape:
        raise ValueError("U,V must be matching two-dimensional arrays")
    if len(args) == 4:
        x,y = args[:2]
        if np.ndim(x) == np.ndim(y) == 2:
            x,y = numeric(x)[0,:], numeric(y)[:,0]
    else:
        x,y = np.arange(1,u.shape[1]+1), np.arange(1,u.shape[0]+1)
    u,v = np.repeat(u[:,:,None],2,axis=2), np.repeat(v[:,:,None],2,axis=2)
    return (x,y,[-1.,1.],u,v,np.zeros_like(u))


def stream2(*args, step=.1, max_steps=10000, direction="forward"):
    if len(args) in (5,7):
        args, spec = args[:-1], np.atleast_1d(args[-1])
        step = spec[0]
        if len(spec) > 1:
            max_steps = int(spec[1])
    if len(args) not in (4,6):
        raise TypeError("expected [X,Y,] U,V,startx,starty")
    lines = stream3(*_planar_field(args[:-2]), *args[-2:], 0, step=step,
                    max_steps=max_steps,direction=direction)
    return [p[:,:2] for p in lines]


@chart
def streamline(*args, ax, step=.1, max_steps=10000, direction="forward", **kwargs):
    if len(args) in (4,5) or (len(args) in (6,7) and np.ndim(args[2]) == 2):
        args = (stream2(*args,step=step,max_steps=max_steps,direction=direction),)
    data = _stream_data(args, step=step, max_steps=max_steps, direction=direction)
    return Graphic(ax, data, **{"color": "C0", **kwargs})


def _derivatives(args):
    coords, u = volume_arrays((*args[:-3], args[-3]))
    x, y, z = _rect_axes(coords)
    return [np.gradient(numeric(a), y, x, z) for a in args[-3:]]


def divergence(*args):
    du, dv, dw = _derivatives(args)
    return du[1] + dv[0] + dw[2]


def curl(*args):
    du, dv, dw = _derivatives(args)
    cx, cy, cz = dw[0]-dv[2], du[2]-dw[1], dv[1]-du[0]
    u, v, w = map(numeric, args[-3:])
    speed = np.sqrt(u*u+v*v+w*w)
    spin = np.divide(cx*u+cy*v+cz*w, 2*speed, out=np.zeros_like(speed), where=speed>0)
    return cx, cy, cz, spin


def interpstreamspeed(*args, scale=1):
    if np.isscalar(args[-1]):
        args, scale = args[:-1], args[-1]
    if scale <= 0:
        raise ValueError("scale must be positive")
    field = _field(args[:-1])
    result = []
    for path in args[-1]:
        path = numeric(path)
        if len(path) < 2:
            result.append(path.copy())
            continue
        speed = vtk_to_numpy(sample(field, poly(path)).GetPointData().GetArray("values"))
        distance = np.linalg.norm(np.diff(path, axis=0), axis=1)
        local = (speed[1:]+speed[:-1])/2
        if np.any(local <= 0):
            raise ValueError("zero or invalid speed along streamline")
        t = np.r_[0, np.cumsum(distance/local)]
        times = np.linspace(0, t[-1], max(2, int(np.ceil(len(path)/scale))))
        result.append(np.column_stack([np.interp(times, t, a) for a in path.T]))
    return result


@chart
def streamtube(*args, radius=None, sides=20, scale=1., ax, **kwargs):
    if len(args) in (3,5,7,10) and np.asarray(args[-1]).shape == (2,):
        args, (scale,sides) = args[:-1], args[-1]
    sides = int(sides)
    widths = None
    precomputed = None
    if len(args) == 4 or (len(args) == 2 and isinstance(args[1],np.ndarray) and args[1].ndim == 3):
        args, precomputed = args[:1], args[1:]
    elif len(args) == 2:
        args, widths = args[:1], args[1]
    data = _stream_data(args)
    tube = vtk.vtkTubeFilter()
    radius = max(data.GetLength(), 1e-12)*.012 if radius is None else radius
    if len(args) in (6, 9):
        coords, _ = volume_arrays((*args[:-6], args[-6]))
        precomputed = (*coords, divergence(*args[:-3]))
    if precomputed is not None:
        div = volume_grid(*volume_arrays(precomputed))
        values = vtk_to_numpy(sample(div, data).GetPointData().GetArray("values"))
        if values.size and np.ptp(values) > 1e-12:
            widths = radius*(.5 + (values-values.min())/np.ptp(values))
    if widths is not None:
        if np.isscalar(widths):
            radius = float(widths)/2
        else:
            w = widths if isinstance(widths,np.ndarray) and widths.ndim == 1 else np.concatenate([np.ravel(a) for a in widths])
            if len(w) != data.GetNumberOfPoints():
                raise ValueError("one width is required per streamline vertex")
            styled = vtk.vtkPolyData()
            styled.ShallowCopy(data)
            styled.GetPointData().SetScalars(array(np.asarray(w)*(scale or 1)/2, "radii"))
            data = styled
            tube.SetVaryRadiusToVaryRadiusByAbsoluteScalar()
    tube.SetRadius(radius*scale if scale else radius)
    tube.SetNumberOfSides(sides)
    tube.CappingOn()
    return Graphic(ax, output(tube, data), **{"color": "C0", "lighting": True, **kwargs})


@chart
def streamribbon(*args, width=None, ax, **kwargs):
    if len(args) > 1 and np.isscalar(args[-1]) and len(args) in (3,4,7,10):
        args, width = args[:-1], args[-1]
    field = None
    if len(args) == 9 or (len(args) == 6 and isinstance(args[0],np.ndarray) and args[0].ndim == 3):
        coords,_ = volume_arrays((*args[:-6],args[-6]))
        field = (*coords,curl(*args[:-3])[-1],np.linalg.norm(args[-6:-3],axis=0))
    elif len(args) in (3,6):
        args, field = args[:1], args[1:]
    twist = None
    if len(args) == 2:
        args, twist = args[:1], args[1]
    data = _stream_data(args)
    paths = _paths(data)
    width = max(data.GetLength(), 1e-12)*.03 if width is None else float(width)
    if field is not None:
        coords,cav = volume_arrays(field[:-1])
        vg = volume_grid(coords,cav)
        vg.GetPointData().AddArray(array(volume_flat(field[-1]),"speed"))
    meshes = vtk.vtkAppendPolyData()
    for i,p in enumerate(paths):
        tangent = np.gradient(p,axis=0)
        tangent /= np.maximum(np.linalg.norm(tangent,axis=1,keepdims=True),1e-30)
        ref = np.eye(3)[np.argmin(np.abs(tangent[0]))]
        normal = np.cross(tangent,ref)
        normal /= np.maximum(np.linalg.norm(normal,axis=1,keepdims=True),1e-30)
        theta = np.zeros(len(p))
        if field is not None:
            pd = sample(vg,poly(p)).GetPointData()
            omega = vtk_to_numpy(pd.GetScalars())
            speed = vtk_to_numpy(pd.GetArray("speed"))
            rates = omega/np.maximum(speed,1e-30)
            theta[1:] = np.cumsum((rates[:-1]+rates[1:])*.5*np.linalg.norm(np.diff(p,axis=0),axis=1))
        elif twist is not None:
            values = twist if len(paths) == 1 and np.asarray(twist).ndim == 1 else twist[i]
            theta[:] = numeric(values)
        normal = normal*np.cos(theta[:,None])+np.cross(tangent,normal)*np.sin(theta[:,None])
        xy = np.stack((p-normal*width/2,p+normal*width/2),axis=1)
        xyz, faces = surface_mesh(*np.moveaxis(xy,-1,0))
        meshes.AddInputData(poly(xyz,faces))
    data = output(meshes) if paths else poly(np.empty((0,3)))
    return Graphic(ax, data, **{"color":"C0","lighting":True,**kwargs})


@chart
def streamslice(*args, density=1, arrows=True, method="linear", ax, **kwargs):
    while args and isinstance(args[-1],str):
        args, option = args[:-1], args[-1]
        if option in ("arrows","noarrows"):
            arrows = option == "arrows"
        elif option in ("linear","nearest","cubic"):
            method = option
        else:
            raise ValueError(f"unknown streamslice option {option!r}")
    if method != "linear":
        raise NotImplementedError("the VTK streamline integrator uses linear interpolation")
    if len(args) in (3,5,7,10):
        args, density = args[:-1], args[-1]
    if density <= 0:
        raise ValueError("density must be positive")
    planar = len(args) in (2,4)
    if planar:
        args = (*_planar_field(args), [], [], [0.])
    field = _field(args[:-3])
    bounds = np.array(field.GetBounds()).reshape(3, 2)
    count = max(2, round(4*np.sqrt(density)))
    starts = [np.linspace(lo, hi, count+2)[1:-1] for lo, hi in bounds]
    result = []
    for i, locations in enumerate(args[-3:]):
        # Integrating the tangential field keeps each trajectory on its slice.
        field_copy = field.NewInstance()
        field_copy.DeepCopy(field)
        vec = vtk_to_numpy(field_copy.GetPointData().GetVectors())
        vec[:, i] = 0
        field_copy.GetPointData().GetVectors().Modified()
        for pos in np.asarray(locations).ravel():
            axes = starts.copy()
            axes[i] = [pos]
            seeds = _xyz(np.meshgrid(*axes))
            data = _trace(field_copy, seeds, direction="both")
            line = Graphic(ax, data, **{"color": "C0", **kwargs})
            result.append(line)
            if arrows not in (False,"noarrows","off"):
                paths = _paths(data)
                if paths:
                    mid = [len(p)//2-1 for p in paths]
                    xyz = np.array([p[j] for p,j in zip(paths,mid)])
                    vec = np.array([p[j+1]-p[j] for p,j in zip(paths,mid)])
                    line.arrows = _glyphs(ax,xyz,vec,vtk.vtkArrowSource(),.25,kwargs)
    if planar:
        ax.set_view(0,90)
    return result
