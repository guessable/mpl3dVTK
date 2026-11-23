"""Line, discrete, distribution and animated charts."""
import numpy as np
import vtk
from matplotlib import colors

from ._geometry import array, cells, line_data, numeric, poly
from .scene import Graphic, _is, chart
from .vectors import _xyz


def _columns(x, y, z):
    a = [np.squeeze(numeric(v)) for v in (x,y,z)]
    matrix = next((v for v in a if v.ndim == 2),None)
    if matrix is not None:
        lengths = {v.size for v in a if v.ndim == 1 and v.size > 1}
        if matrix.shape[0] not in lengths and matrix.shape[1] in lengths:
            a = [v.T if v.ndim == 2 else v for v in a]
            matrix = matrix.T
        a = [v[:,None] if v.ndim == 1 else v for v in a]
    a = np.broadcast_arrays(*a)
    return np.stack([v.T if v.ndim == 2 else np.atleast_1d(v)[None, :] for v in a], axis=-1)


def _is_selector(value):
    return isinstance(value,str) or (isinstance(value,(tuple,list)) and len(value) and
                                     all(isinstance(v,str) for v in value))


def _table_columns(table, selector):
    if isinstance(selector,str):
        return numeric(table[selector])
    return np.column_stack([numeric(table[name]) for name in selector])


@chart
def plot3(x, y, z, *rest, ax, **kwargs):
    """Plot vectors, matrix series, table columns, or successive XYZ groups."""
    if _is_selector(y) and _is_selector(z) and rest and _is_selector(rest[0]):
        table, selectors, rest = x, (y,z,rest[0]), rest[1:]
        x,y,z = [_table_columns(table, v) for v in selectors]
    opts = kwargs.copy()
    if rest and isinstance(rest[0], str):
        spec, rest = rest[0], rest[1:]
        from matplotlib.axes._base import _process_plot_format
        linestyle, marker, color = _process_plot_format(spec)
        if color is not None:
            opts.setdefault("color", color)
        if linestyle == "None":
            linestyle = "none"
    else:
        linestyle, marker = "-", None
    linestyle = opts.pop("linestyle", linestyle)
    marker = opts.pop("marker", marker)
    size = opts.pop("markersize", 6)
    markerface = opts.pop("markerfacecolor", "auto")
    markeredge = opts.pop("markeredgecolor", "auto")
    paths = _columns(x, y, z)
    handles = []
    fixed_color = opts.pop("color", None)
    for path in paths:
        color = fixed_color if fixed_color is not None else ax._get_lines.get_next_color()
        if linestyle not in (None, "", "none", "None"):
            line = Graphic(ax, line_data([path]), color=color, linestyle=linestyle, **opts)
            handles.append(line)
        if marker not in (None, "", "none", "None"):
            mc = color if _is(markerface,"auto","none") else markerface
            if _is(markerface,"none") and not _is(markeredge,"auto","none"):
                mc = markeredge
            handles.append(scatter3(ax, *path.T, float(size)**2, marker, color=mc))
    if rest:
        group = plot3(ax, *rest, **kwargs)
        handles.extend(group if isinstance(group,list) else [group])
    return handles[0] if len(handles) == 1 else handles


@chart
def fplot3(fx, fy, fz, interval=(-5,5), *, samples=201, ax, **kwargs):
    t = np.linspace(*interval, samples)
    return plot3(ax, *(np.broadcast_to(f(t), t.shape) for f in (fx,fy,fz)), **kwargs)


@chart
def line(*args, ax, xdata=None, ydata=None, zdata=0, **kwargs):
    """Add a primitive line and preserve existing scene objects."""
    if not args:
        args = (xdata if xdata is not None else [0,1], ydata if ydata is not None else [0,1], zdata)
    elif len(args) == 2:
        args = (*args,zdata)
    return plot3(ax,*args,**kwargs)


@chart
def scatter3(x, y, z, s=36, c=None, *flags, ax, **kwargs):
    marker = kwargs.pop("marker","o")
    filled = False
    if _is(s, "filled"):
        filled, s = True, 36
    elif isinstance(s,str):
        s,c = 36,s
    if isinstance(c,str) and c in ("o","+","*",".","x","s","d","^","v",">","<","p","h","square","diamond"):
        marker,c = c,None
    if _is(c,"filled"):
        filled,c = True,None
    for flag in flags:
        if _is(flag,"filled"):
            filled = True
        elif isinstance(flag,str):
            marker = flag
        else:
            raise TypeError("expected a marker or 'filled' after C")
    point_size = kwargs.pop("markersize",None)
    edge = kwargs.pop("markeredgecolor","auto")
    face = kwargs.pop("markerfacecolor","auto" if filled else "none")
    if not _is(face, "auto", "none") or not _is(edge, "auto", "none"):
        kwargs.setdefault("color", edge if _is(face, "auto", "none") else face)
    xyz = _xyz((x,y,z))
    valid = np.isfinite(xyz).all(axis=1)
    if isinstance(c, str) or (isinstance(c, tuple) and colors.is_color_like(c)):
        kwargs["color"], c = c, None
    if c is not None:
        c = np.asarray(c)
        c = c.reshape(-1, c.shape[-1]) if c.ndim > 1 and c.size != len(xyz) else c.ravel()
        c = c[valid]
    else:
        kwargs.setdefault("color", "C0")
    sizes = np.asarray(s if point_size is None else float(point_size)**2, dtype=float)
    if sizes.size == 0:
        sizes = np.array(36.)
    if not np.isfinite(sizes).all() or np.any(sizes < 0):
        raise ValueError("marker areas must be finite and nonnegative")
    sizes = np.broadcast_to(sizes.ravel(), (len(xyz),))[valid]
    data = poly(xyz[valid])
    data.SetVerts(cells(np.arange(len(sizes)).reshape(-1,1)))
    if marker in ("o",".") and (not sizes.size or np.all(sizes == sizes[0])):
        h = Graphic(ax, data, c, size=np.sqrt(sizes[0]) if sizes.size else 1, **kwargs)
        if marker == "o":
            h.actor.GetProperty().RenderPointsAsSpheresOn()
        return h
    # Glyph dimensions are in scene units for per-point size and shape.
    source = vtk.vtkGlyphSource2D()
    shapes = {"o":"Circle",".":"Vertex","+":"Cross","x":"Cross","*":"Star",
              "s":"Square","square":"Square","d":"Diamond","diamond":"Diamond",
              "^":"Triangle","v":"Triangle",">":"Triangle","<":"Triangle","p":"Star","h":"Circle"}
    if marker not in shapes:
        raise ValueError(f"unsupported scatter marker {marker!r}")
    name = shapes[marker]
    if name == "Star" and not hasattr(source,"SetGlyphTypeToStar"):
        name = "ThickCross"
    getattr(source,"SetGlyphTypeTo"+name)()
    source.SetFilled(filled and marker not in ("+","x","*","."))
    source.SetRotationAngle({"x":45,"v":180,">":-90,"<":90}.get(marker,0))
    data.GetPointData().AddArray(array(np.sqrt(sizes), "diameter"))
    mapper = vtk.vtkGlyph3DMapper()
    mapper.SetSourceConnection(source.GetOutputPort())
    mapper.SetScaleArray("diameter")
    mapper.SetScaleModeToScaleByMagnitude()
    mapper.SetScaleFactor(max(data.GetLength(), 1e-9)/350)
    transform = vtk.vtkTransform()
    billboard = vtk.vtkTransformFilter()
    billboard.SetTransform(transform)
    billboard.SetInputConnection(source.GetOutputPort())
    mapper.SetSourceConnection(billboard.GetOutputPort())
    mapper.OrientOff()
    h = Graphic(ax, data, c, mapper=mapper, **kwargs)
    h._marker_transform = transform
    return h


@chart
def bubblechart3(x, y, z, sizes, c=None, *, ax, **kwargs):
    sizes = numeric(sizes)
    finite = sizes[np.isfinite(sizes)]
    if not finite.size:
        raise ValueError("bubble sizes must contain finite values")
    scaled = 30 + 400*(sizes-finite.min())/max(np.ptp(finite), 1e-30)
    return scatter3(ax, x, y, z, scaled, c, **kwargs)


@chart
def swarmchart3(x, y, z, s=36, c=None, *, ax, width=.45, **kwargs):
    x, y, z = _xyz((x,y,z)).T
    x = x.copy()
    for value in np.unique(x):
        ids = np.flatnonzero(x == value)
        if len(ids) < 2:
            continue
        # Points close in the y/z plane get alternating horizontal slots.
        plane = np.column_stack((y[ids], z[ids]))
        extent = np.ptp(plane, axis=0)
        bins = np.floor((plane-plane.min(axis=0))/np.where(extent>0, extent, 1)*8)
        for group in np.unique(bins, axis=0):
            members = ids[np.all(bins == group, axis=1)]
            if len(members) > 1:
                x[members] += np.linspace(-width/2, width/2, len(members))
    return scatter3(ax, x, y, z, s, c, **kwargs)


@chart
def stem3(*args, ax, baseline=0, **kwargs):
    spec = args[-1] if args and isinstance(args[-1],str) else None
    if spec is not None:
        from matplotlib.axes._base import _process_plot_format
        args = args[:-1]
        style, marker, color = _process_plot_format(spec)
        if style not in (None,"None"):
            kwargs.setdefault("linestyle",style)
        if marker not in (None,"None"):
            kwargs.setdefault("marker",marker)
        if color is not None:
            kwargs.setdefault("color",color)
    if len(args) == 1:
        z = numeric(args[0])
        if z.ndim == 1:
            x, y = np.arange(1,len(z)+1), np.ones_like(z)
        else:
            y, x = np.indices(z.shape)+1
    else:
        x, y, z = args
    xyz = _xyz((x,y,z))
    bottom = xyz.copy()
    bottom[:,2] = baseline
    paths = np.stack((bottom,xyz), axis=1)
    marker = kwargs.pop("marker","o")
    marker_size = kwargs.pop("markersize",6)
    marker_face = kwargs.pop("markerfacecolor","auto")
    stems = Graphic(ax, line_data(paths), **{"color":"C0", **kwargs})
    if marker in (None,"","none","None"):
        return stems
    return stems, scatter3(ax, *xyz.T, marker_size**2, marker, markerfacecolor=marker_face,
                           color=kwargs.get("color", "C0"))


def _bars(ax, x, y, base, top, wx, wy, horizontal, opts):
    corners = np.array([[0,0,0],[1,0,0],[1,1,0],[0,1,0],
                        [0,0,1],[1,0,1],[1,1,1],[0,1,1]])
    xx, yy, low, high, wx, wy = np.broadcast_arrays(x,y,base,top,wx,wy)
    valid = np.isfinite(xx+yy+low+high+wx+wy)
    starts = np.column_stack(((xx-wx/2)[valid], (yy-wy/2)[valid], low[valid]))
    spans = np.column_stack((wx[valid], wy[valid], (high-low)[valid]))
    xyz = (starts[:,None,:] + spans[:,None,:]*corners).reshape(-1,3)
    if horizontal:
        xyz = xyz[:,[2,1,0]]
    sides = np.array([[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]])
    faces = (8*np.arange(len(starts))[:,None,None]+sides).reshape(-1,4)
    return Graphic(ax, poly(xyz, faces), np.repeat(high[valid],6), association="cell",
                   **{"edgecolor":"black", **opts})


def _barplot(args, ax, width, style, horizontal, kwargs):
    if isinstance(args[-1], str):
        args, style = args[:-1], args[-1]
    if len(args) > 1 and np.isscalar(args[-1]):
        args, width = args[:-1], args[-1]
    z = np.array(args[-1], dtype=float, ndmin=1)
    if z.ndim == 1:
        z = z[:,None]
    y = np.arange(1,len(z)+1) if len(args) == 1 else numeric(args[0])
    cols = z.shape[1]
    x,y = np.meshgrid(np.arange(1,cols+1),y)
    base = np.zeros_like(z)
    if style == "stacked":
        pos, neg = np.maximum(z,0), np.minimum(z,0)
        base = np.where(z>=0, np.cumsum(pos,axis=1)-pos, np.cumsum(neg,axis=1)-neg)
        x = np.ones_like(x)
    elif style == "grouped":
        y = y + (x-(cols+1)/2)*width/cols
        x = np.ones_like(x)
    elif style != "detached":
        raise ValueError("choose detached, grouped or stacked")
    return _bars(ax,x,y,base,base+z,width,width/cols if style=="grouped" else width,horizontal,kwargs)


@chart
def bar3(*args, width=.8, style="detached", ax, **kwargs):
    return _barplot(args, ax, width, style, False, kwargs)


@chart
def bar3h(*args, width=.8, style="detached", ax, **kwargs):
    return _barplot(args, ax, width, style, True, kwargs)


@chart
def histogram2(x, y, bins=10, *, ax, num_bins=None, x_bin_edges=None, y_bin_edges=None,
               normalization="count", display_style="bar3", show_empty_bins=True, **kwargs):
    if num_bins is not None:
        bins = num_bins
    if x_bin_edges is not None or y_bin_edges is not None:
        nx,ny = (bins,bins) if np.ndim(bins) == 0 else bins
        bins = (nx if x_bin_edges is None else x_bin_edges, ny if y_bin_edges is None else y_bin_edges)
    x,y = [numeric(a).ravel() for a in (x,y)]
    if x.shape != y.shape:
        raise ValueError("histogram coordinates must have the same length")
    valid = np.isfinite(x) & np.isfinite(y)
    count, xe, ye = np.histogram2d(x[valid],y[valid],bins)
    area = np.diff(xe)[:,None]*np.diff(ye)[None,:]
    n = max(count.sum(),1)
    if normalization in ("probability", "pdf", "cdf"):
        count = count/n
    if normalization in ("countdensity", "pdf"):
        count = count/area
    if normalization in ("cumcount","cdf"):
        count = count.cumsum(axis=0).cumsum(axis=1)
    if normalization not in ("count","probability","pdf","cdf","countdensity","cumcount"):
        raise ValueError("unknown histogram normalization")
    xx, yy = np.meshgrid((xe[1:]+xe[:-1])/2, (ye[1:]+ye[:-1])/2, indexing="ij")
    if show_empty_bins in (False,"off"):
        count = np.where(count == 0,np.nan,count)
    if display_style == "tile":
        from .surfaces import pcolor
        colors = np.pad(count,((0,1),(0,1)),mode="edge")
        return pcolor(ax,xe,ye,colors.T,**kwargs)
    if display_style != "bar3":
        raise ValueError("DisplayStyle must be bar3 or tile")
    h = _bars(ax,xx,yy,0,count,np.diff(xe)[:,None],np.diff(ye)[None,:],False,kwargs)
    h.values, h.x_bin_edges, h.y_bin_edges = count, xe, ye
    return h


@chart
def pie3(values, explode=None, labels=None, *, ax, **kwargs):
    from .scene import text
    val = numeric(values).ravel()
    if np.any(val < 0) or not val.sum() > 0:
        raise ValueError("pie values must be nonnegative with positive sum")
    if labels is None and explode is not None and np.asarray(explode).dtype.kind in "US":
        labels, explode = explode, None
    if labels is not None and len(labels) != len(val):
        raise ValueError("provide one label per pie wedge")
    if labels is None:
        labels = [f"{v/max(val.sum(),1):.0%}" for v in val]
    gaps = np.zeros(len(val)) if explode is None else np.broadcast_to(explode,val.shape)
    end = np.r_[0, np.cumsum(val/max(val.sum(),1))*2*np.pi]
    result = []
    for i, (a,b) in enumerate(zip(end,end[1:])):
        if a == b:
            continue
        theta = np.linspace(a,b,max(3,round((b-a)*24)+1))
        mid = (a+b)/2
        offset = .12*bool(gaps[i])*np.array([np.cos(mid),np.sin(mid)])
        rim = np.column_stack((np.cos(theta),np.sin(theta)))
        base = np.vstack(([0,0],rim))+offset
        n = len(base)
        xyz = np.vstack([np.column_stack((base,np.full(n,h))) for h in (0,.25)])
        j = np.arange(1,n-1)
        top = np.column_stack((np.full(len(j),n),j+n,j+n+1))
        edge = np.arange(n)
        nxt = (edge+1)%n
        faces = np.vstack((top, top[:,::-1]-n, np.column_stack((edge,nxt,nxt+n)),
                           np.column_stack((edge,nxt+n,edge+n))))
        result.append(Graphic(ax,poly(xyz,faces), **{"color":f"C{i%10}","lighting":True,**kwargs}))
        label = text(*(1.12*np.array([np.cos(mid),np.sin(mid)])+offset),.25,labels[i],ax=ax)
        result[-1].annotations.append(label)
    return result


class AnimatedLine(Graphic):
    """VTK line updated in batches at Matplotlib draw time."""
    def __init__(self, ax, maximum_num_points, **kwargs):
        if maximum_num_points is not None and (maximum_num_points < 1 or int(maximum_num_points) != maximum_num_points):
            raise ValueError("MaximumNumPoints must be a positive integer")
        self.maximum_num_points = None if maximum_num_points is None else int(maximum_num_points)
        self._history = np.empty((0,3))
        self._pending = []
        super().__init__(ax, line_data([]), **{"color":"C0", **kwargs})

    def addpoints(self, x, y, z=0):
        self._pending.append(_xyz((x,y,z)))
        self.axes.stale = True

    def _flush(self):
        if not self._pending:
            return
        self._history = np.concatenate([self._history,*self._pending])
        if self.maximum_num_points is not None:
            self._history = self._history[-self.maximum_num_points:].copy()
        self._pending.clear()
        self.data.ShallowCopy(line_data([self._history]))
        self.axes._limits_dirty = True

    def getpoints(self):
        self._flush()
        return tuple(a.copy() for a in self._history.T)

    def clearpoints(self):
        self._history = np.empty((0,3))
        self._pending = [self._history]
        self._flush()
        self.axes.stale = True


@chart
def animatedline(*args, ax, maximum_num_points=None, **kwargs):
    """Create a 3-D animated line with an optional bounded point history."""
    if len(args) not in (0,2,3):
        raise TypeError("expected no data, X,Y, or X,Y,Z")
    h = AnimatedLine(ax, maximum_num_points, **kwargs)
    if args:
        h.addpoints(*args)
        h._flush()
    return h


def addpoints(handle, x, y, z=0):
    handle.addpoints(x,y,z)


def getpoints(handle):
    return handle.getpoints()


def clearpoints(handle):
    handle.clearpoints()


class Motion:
    """Timer-driven animation with explicit frame selection for batch rendering."""
    def __init__(self, handle, frames, update, interval):
        self.handle = handle
        self.frames = frames
        self.update = update
        self.index = 0
        self.timer = handle.axes.figure.canvas.new_timer(interval=interval)
        self.timer.add_callback(self._advance)
        self.set_frame(0)
        self.timer.start()

    def set_frame(self, index):
        self.index = int(index) % self.frames
        self.update(self.index)
        self.handle.axes.stale = True

    def _advance(self):
        if self.handle not in self.handle.axes.handles or self.index+1 == self.frames:
            self.timer.stop()
            return
        self.set_frame(self.index+1)
        self.handle.axes.figure.canvas.draw_idle()


@chart
def comet3(*args, ax, interval=30, tail=.1, **kwargs):
    if len(args) == 4:
        args, tail = args[:3], args[3]
    if len(args) == 1:
        z = numeric(args[0]).ravel()
        xyz = _xyz((np.ones_like(z),np.arange(1,len(z)+1),z))
    else:
        xyz = _xyz(args)
    if not len(xyz) or not 0 < tail <= 1:
        raise ValueError("expected a nonempty trajectory and tail in (0,1]")
    body = Graphic(ax, line_data([xyz]), **{"color":"C0", **kwargs})
    recent = Graphic(ax, line_data([xyz]), color="C1", linewidth=2)
    head = scatter3(ax, *xyz[:1].T, color="C1")
    body._bounds_override = tuple(np.column_stack((xyz.min(axis=0),xyz.max(axis=0))).ravel())
    def advance(i):
        body.data.ShallowCopy(line_data([xyz[:i+1]]))
        recent.data.ShallowCopy(line_data([xyz[max(0,i-round(tail*len(xyz))):i+1]]))
        head.data.GetPoints().SetPoint(0, *xyz[i])
        head.data.GetPoints().Modified()
    anim = Motion(body, len(xyz), advance, interval)
    body.animation = anim
    return anim


@chart
def streamparticles(paths, n=20, *, ax, interval=30, **kwargs):
    paths = [numeric(p) for p in paths if len(p)]
    if not paths or int(n) < 1:
        raise ValueError("provide nonempty paths and a positive particle count")
    offsets = [np.linspace(0,len(p),max(1,round(n*len(p)/sum(map(len,paths)))),endpoint=False).astype(int) for p in paths]
    def positions(i):
        return np.concatenate([p[(idx+i)%len(p)] for p,idx in zip(paths,offsets)])
    h = scatter3(ax,*positions(0).T, **kwargs)
    all_xyz = np.concatenate(paths)
    h._bounds_override = tuple(np.column_stack((all_xyz.min(axis=0),all_xyz.max(axis=0))).ravel())
    def advance(i):
        h.data.GetPoints().SetData(array(positions(i),"coordinates"))
    anim = Motion(h,max(map(len,paths)),advance,interval)
    h.animation = anim
    return anim
