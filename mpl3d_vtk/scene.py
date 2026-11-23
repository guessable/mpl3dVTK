"""Figure integration. All geometry, depth testing and lighting live in VTK."""
from functools import wraps

import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.artist import Artist
from matplotlib.cm import ScalarMappable
from matplotlib.colors import BoundaryNorm, ListedColormap, to_rgb, to_rgba

from ._geometry import array, numeric, points, vertices
from ._axes import VtkAxes


def _is(value, *tokens):
    return isinstance(value, str) and value.lower() in tokens


_PROPERTIES = {
    "alphadata": "alphadata", "alphadatamapping": "alphadatamapping",
    "ambientstrength": "ambientstrength", "autoscale": "autoscale",
    "autoscalefactor": "autoscalefactor", "basevalue": "baseline",
    "cdata": "cdata", "cdatamapping": "cdatamapping", "color": "color",
    "diffusestrength": "diffusestrength", "displayname": "label",
    "edgealpha": "edgealpha", "edgecolor": "edgecolor", "edgelighting": "edgelighting",
    "facealpha": "alpha", "facecolor": "facecolor", "facelighting": "lighting",
    "faces": "faces", "facevertexcdata": "facevertexcdata",
    "linewidth": "linewidth", "linestyle": "linestyle", "marker": "marker",
    "markeredgecolor": "markeredgecolor", "markerfacecolor": "markerfacecolor",
    "markersize": "markersize", "maxheadsize": "maxheadsize", "showarrowhead": "showarrowhead",
    "maximumnumpoints": "maximum_num_points", "meshdensity": "samples",
    "showcontour": "showcontour", "specularstrength": "specularstrength",
    "specularexponent": "specularexponent", "vertices": "vertices",
    "visible": "visible", "xdata": "xdata", "ydata": "ydata", "zdata": "zdata",
    "numbins": "num_bins", "xbinedges": "x_bin_edges", "ybinedges": "y_bin_edges",
    "normalization": "normalization", "displaystyle": "display_style", "showemptybins": "show_empty_bins",
    "jitter": "jitter", "xjitter": "jitter", "xjitterwidth": "width",
    "alphamap": "alphamap", "renderingstyle": "rendering_style",
    "framesize": "frame_size", "colormap": "cmap", "showframelabels": "show_frame_labels",
    "nodecolor": "node_color", "nodelabel": "node_label",
    "showarrows": "show_arrows", "layout": "layout", "interpolation": "interpolation",
}


def _property_name(name):
    return _PROPERTIES.get(name.lower(), name)


def _line_style(prop, style):
    patterns = {"-": 0xFFFF, "--": 0xF0F0, ":": 0xAAAA, "-.": 0xF4F4, "none": 0}
    if style not in patterns:
        raise ValueError("LineStyle must be '-', '--', ':', '-.' or 'none'")
    prop.SetLineStipplePattern(patterns[style])


def _cmap(value):
    if isinstance(value, (str, mpl.colors.Colormap)):
        return mpl.colormaps.get_cmap(value)
    rgb = np.asarray(value, dtype=float)
    if rgb.ndim != 2 or rgb.shape[1] not in (3,4) or not len(rgb):
        raise ValueError("a colormap must be a Matplotlib name or an (n, 3/4) color array")
    return ListedColormap(rgb)


class Graphic(Artist, ScalarMappable):
    """Returned plot handle. actor, mapper and data expose the native VTK objects."""
    def __init__(self, ax, data, values=None, association="point", mapper=None, **options):
        Artist.__init__(self)
        names = {"edgecolors": "edgecolor", "facealpha": "alpha", "linewidths": "linewidth",
                 "facelighting": "lighting", "markersize": "size", "lw": "linewidth"}
        opts = {names.get(k.lower(), k.lower()): v for k, v in options.items()}
        self.axes = ax
        self.data = data
        self._geometry_key = None
        self.actor = vtk.vtkActor()
        self.mapper = vtk.vtkPolyDataMapper() if mapper is None else mapper
        self.mapper.SetInputData(data)
        self.actor.SetMapper(self.mapper)
        self.association = association
        prop = self.actor.GetProperty()
        self.face = opts.pop("facecolor", "interp")
        self.edge = opts.pop("edgecolor", "none")
        self._color = opts.pop("color", None)
        self._wireframe = opts.pop("representation", "surface") == "wireframe"
        self._apply_colors()
        alpha = opts.pop("alpha", None)
        self._alpha_mode = alpha if _is(alpha, "flat", "interp") else None
        self.set_alpha(None if self._alpha_mode else alpha)
        self._alpha_data = opts.pop("alphadata", None)
        self._alpha_mapping = opts.pop("alphadatamapping", "none")
        self._cdata_mapping = opts.pop("cdatamapping", "scaled")
        if self._alpha_mapping not in ("none", "scaled", "direct") or self._cdata_mapping not in ("scaled", "direct"):
            raise ValueError("invalid AlphaDataMapping or CDataMapping")
        self.set_linewidth(opts.pop("linewidth", 1))
        prop.SetPointSize(float(opts.pop("size", 5)))
        self.set_lighting(opts.pop("lighting", False))
        prop.SetAmbient(float(opts.pop("ambientstrength", .22)))
        prop.SetDiffuse(float(opts.pop("diffusestrength", .78)))
        prop.SetSpecular(float(opts.pop("specularstrength", .12)))
        prop.SetSpecularPower(float(opts.pop("specularexponent", 18)))
        if "edgealpha" in opts:
            prop.SetEdgeOpacity(float(opts.pop("edgealpha")))
        if "linestyle" in opts:
            _line_style(prop, opts.pop("linestyle"))
        visible = opts.pop("visible", True)
        self.set_visible(not _is(visible, "off") and bool(visible))
        cmap = _cmap(opts.pop("cmap", ax.default_cmap))
        norm = opts.pop("norm", None)
        clim = opts.pop("clim", None)
        opts_label = opts.pop("label", None)
        vmin, vmax = opts.pop("vmin", None), opts.pop("vmax", None)
        if clim is None and (vmin is not None or vmax is not None):
            clim = (vmin,vmax)
        if clim is None and self._cdata_mapping == "scaled" and norm is None:
            clim = ax.color_limits
        if opts:
            raise TypeError(f"unknown graphics properties: {', '.join(opts)}")
        self.set_label(opts_label)
        if self._cdata_mapping == "direct":
            if norm is not None or clim is not None:
                raise ValueError("direct CDataMapping uses one-based colormap indices")
            norm = BoundaryNorm(np.arange(cmap.N+1)+.5, cmap.N, clip=True)
        ScalarMappable.__init__(self, norm=norm, cmap=cmap)
        self._values = None
        self._bounds_override = None
        self.annotations = []
        if values is None and data.GetPointData().GetScalars():
            values = vtk_to_numpy(data.GetPointData().GetScalars())
        if values is not None:
            self.set_cdata(values, _refresh=False)
        if clim is not None:
            self.set_clim(*clim)
        self.callbacks.connect("changed", self._refresh)
        self._refresh()
        ax.renderer.AddActor(self.actor)
        ax.add_artist(self)
        ax.handles.append(self)
        ax._limits_dirty = True
        ax.stale = True

    def raw_bounds(self):
        # Glyph mapper bounds include the instanced geometry.
        if self._bounds_override is not None:
            return self._bounds_override
        if self.mapper.GetInput() is self.data:
            return self.mapper.GetBounds()
        return self.data.GetBounds()

    def sync_geometry(self, transforms, nonlinear):
        self.actor.SetVisibility(self.get_visible())
        if not any(nonlinear):
            if self._geometry_key is not None:
                self.mapper.SetInputData(self.data)
                self._geometry_key = None
            return
        key = (self.data.GetMTime(),tuple(str(t) for t in transforms))
        if key != self._geometry_key:
            transformed = vtk.vtkPolyData()
            transformed.ShallowCopy(self.data)
            xyz = self.vertices
            for i in range(3):
                if nonlinear[i]:
                    xyz[:,i] = transforms[i].transform(xyz[:,i])
            transformed.SetPoints(points(xyz))
            self.mapper.SetInputData(transformed)
            self._geometry_key = key

    def draw(self, renderer):
        # The viewport composites every actor together with one depth buffer.
        self.stale = False

    def set_alpha(self, alpha):
        super().set_alpha(alpha)
        self.actor.GetProperty().SetOpacity(1 if alpha is None else alpha)

    def set_visible(self, visible):
        super().set_visible(visible)
        for companion in getattr(self,"_companions",()):
            companion.set_visible(visible)

    def _apply_colors(self):
        prop = self.actor.GetProperty()
        self.wire = self._wireframe or _is(self.face, "none")
        prop.SetRepresentationToWireframe() if self.wire else prop.SetRepresentationToSurface()
        prop.SetEdgeVisibility(not self.wire and not _is(self.edge, "none"))
        solid_edge = not _is(self.edge, "none", "flat", "interp")
        if solid_edge:
            prop.SetEdgeColor(to_rgb(self.axes._series_color(self.edge)))
        self.constant_color = self._color
        if not _is(self.face, "interp", "flat", "none"):
            self.constant_color = self.face
        if self.wire and solid_edge:
            self.constant_color = self.edge
        self.constant_color = self.axes._series_color(self.constant_color)
        prop.SetColor(to_rgb(self.constant_color) if self.constant_color is not None else (1,1,1))

    def set_color(self, color):
        self._color = color
        if not _is(self.face, "flat", "interp", "none"):
            self.face = color
        self._apply_colors()
        self._refresh()

    def set_facecolor(self, color):
        self.face = color
        self._apply_colors()
        self._refresh()

    def set_edgecolor(self, color):
        self.edge = color
        self._apply_colors()
        self._refresh()

    def set_linewidth(self, width):
        self.actor.GetProperty().SetLineWidth(float(width))
        self.stale = True

    def set_lighting(self, light):
        prop = self.actor.GetProperty()
        prop.SetLighting(bool(light) and not _is(light, "none", "off"))
        interpolation = light.title() if _is(light, "flat", "gouraud", "phong") else "Phong"
        getattr(prop, "SetInterpolationTo" + interpolation)()
        if prop.GetLighting() and hasattr(self, "grid_shape"):
            self.update_surface_normals()
        self.stale = True

    def update_surface_normals(self):
        if not self.actor.GetProperty().GetLighting():
            return
        from .surfaces import _normals
        x, y, z = vertices(self.data).T.reshape((3,) + self.grid_shape)
        normals = _normals(x,y,z).reshape(-1,3)
        invalid = ~np.isfinite(normals).all(axis=1)
        normals[invalid] = (0,0,1)
        self.data.GetPointData().SetNormals(array(normals, "normals"))

    def set_cdata(self, values, *, _refresh=True):
        values = np.asarray(values)
        count = self.data.GetNumberOfPoints() if self.association == "point" else self.data.GetNumberOfCells()
        if values.size == count:
            values = values.reshape(count)
        elif values.ndim >= 2 and values.shape[-1] in (3, 4) and values.size == count * values.shape[-1]:
            values = values.reshape(count, -1)
        else:
            raise ValueError(f"CData must contain {count} scalars or RGB(A) colors")
        if values.ndim == 1:
            self._values = numeric(values)
            ScalarMappable.set_array(self, self._values)
        else:
            self._values = values
            ScalarMappable.set_array(self, None)
        if _refresh:
            self._refresh()
        return self

    def set_array(self, values):
        if values is not None:
            values = numeric(values).ravel()
            size = self.data.GetNumberOfPoints() if self.association == "point" else self.data.GetNumberOfCells()
            if values.size != size:
                raise ValueError(f"expected {size} values for the VTK geometry")
        self._values = values
        ScalarMappable.set_array(self, values)
        self._refresh()

    def _refresh(self, *_):
        varying_alpha = self._alpha_mode is not None and self._alpha_data is not None
        if (self.constant_color is not None or self._values is None) and not varying_alpha:
            self.mapper.ScalarVisibilityOff()
        else:
            values = self._values
            if self.constant_color is not None or values is None:
                count = self.data.GetNumberOfPoints() if self.association == "point" else self.data.GetNumberOfCells()
                color = self.constant_color if self.constant_color is not None else "white"
                rgba = np.broadcast_to(np.round(255*np.array(to_rgba(color))).astype(np.uint8), (count,4)).copy()
            elif values.ndim == 1:
                rgba = self.to_rgba(values, bytes=True)
            elif values.dtype == np.uint8:
                rgba = values
            else:
                rgba = (np.clip(values, 0, 1) * 255).round().astype(np.uint8)
            if varying_alpha:
                alpha = numeric(self._alpha_data).ravel()
                alpha = np.broadcast_to(alpha, (len(rgba),))
                if self._alpha_mapping == "scaled":
                    lo, hi = self.axes.alpha_limits
                    alpha = (alpha-lo)/(hi-lo)
                elif self._alpha_mapping == "direct":
                    alpha = (alpha-1)/63
                rgba = np.column_stack((rgba[:,:3], np.nan_to_num(np.clip(alpha,0,1))*255)).astype(np.uint8)
            assoc = self.association
            if (_is(self.face, "flat") or self._alpha_mode == "flat") and assoc == "point" and self.data.GetNumberOfPolys() == self.data.GetNumberOfCells() and self.data.GetNumberOfCells():
                polys = self.data.GetPolys()
                ids = vtk_to_numpy(polys.GetConnectivityArray())
                starts = vtk_to_numpy(polys.GetOffsetsArray())[:-1]
                rgba, assoc = rgba[ids[starts]], "cell"
            attrs = self.data.GetPointData() if assoc == "point" else self.data.GetCellData()
            attrs.AddArray(array(rgba, "display_rgba"))
            mode = self.mapper.SetScalarModeToUsePointFieldData if assoc == "point" else self.mapper.SetScalarModeToUseCellFieldData
            mode()
            self.mapper.SelectColorArray("display_rgba")
            self.mapper.SetColorModeToDirectScalars()
            self.mapper.ScalarVisibilityOn()
        self.axes.stale = True

    @property
    def vertices(self):
        return vertices(self.data).copy()

    @property
    def faces(self):
        cells = self.data.GetPolys()
        ids = vtk_to_numpy(cells.GetConnectivityArray())
        offsets = vtk_to_numpy(cells.GetOffsetsArray())
        sizes = np.diff(offsets)
        if not len(sizes):
            return np.empty((0, 3), dtype=int)
        if np.all(sizes == sizes[0]):
            return ids.reshape(-1, sizes[0]).copy()
        return [ids[a:b].copy() for a,b in zip(offsets, offsets[1:])]

    def set_zdata(self, z):
        """Update a gridded surface and keep its VTK point buffer when possible."""
        from ._geometry import cells, numeric, surface_mesh
        z = numeric(z)
        if z.shape != getattr(self, "grid_shape", None):
            raise ValueError("Z must match the original surface matrix")
        xyz = vertices(self.data)
        changed_mask = np.any(np.isfinite(xyz[:,2]) != np.isfinite(z.ravel()))
        xyz[:,2] = z.ravel()
        self.data.GetPoints().Modified()
        if changed_mask:
            _, faces = surface_mesh(xyz[:,0].reshape(z.shape), xyz[:,1].reshape(z.shape), z)
            self.data.SetPolys(cells(faces))
        self.update_surface_normals()
        if self.color_tracks_height:
            self.set_cdata(z)
        elif changed_mask:
            self._refresh()
        self.axes._limits_dirty = True
        self.axes.stale = True
        return self

    def remove(self):
        if self.axes is not None and self in self.axes.handles:
            for companion in getattr(self,"_companions",()):
                companion.remove()
            for annotation in self.annotations:
                annotation.remove()
            self.annotations.clear()
            self.axes.renderer.RemoveActor(self.actor)
            self.axes.handles.remove(self)
            self.axes._limits_dirty = True
            self.axes.stale = True
            Artist.remove(self)


def gca():
    fig = plt.gcf()
    if fig.axes:
        current = fig.gca()
        if isinstance(current, VtkAxes):
            return current
    return fig.add_subplot(projection=VtkAxes.name)


def chart(fn):
    """Accept a leading axes or ax= and apply hold once to composite plots."""
    @wraps(fn)
    def draw(*args, ax=None, **kwargs):
        if args and isinstance(args[0], VtkAxes):
            ax, args = args[0], args[1:]
        split = next((i for i,v in enumerate(args[:-1]) if isinstance(v,str) and v.lower() in _PROPERTIES), len(args))
        if split < len(args):
            pairs = args[split:]
            if len(pairs) % 2 or any(not isinstance(k,str) or k.lower() not in _PROPERTIES for k in pairs[::2]):
                raise TypeError("use graphics property name/value pairs")
            kwargs = {**dict(zip(pairs[::2],pairs[1::2])), **kwargs}
            args = args[:split]
        kwargs = {_property_name(k):v for k,v in kwargs.items()}
        ax = gca() if ax is None else ax
        if not isinstance(ax, VtkAxes):
            raise TypeError("use an axes with projection='vtk3d'")
        outer = not ax._inside_plot
        primitive = fn.__name__ in ("surface", "line", "animatedline")
        existing = ax.handles.copy() if outer and not ax.holding and not primitive else []
        old_count = len(ax.handles)
        ax._inside_plot = True
        try:
            result = fn(*args, ax=ax, **kwargs)
        except Exception:
            for handle in ax.handles[old_count:]:
                handle.remove()
            raise
        finally:
            ax._inside_plot = not outer
        for handle in existing:
            handle.remove()
        if outer and ax._limits_dirty:
            ax.fit()
        return result
    # Axes.patch is Matplotlib's own background artist.
    if fn.__name__ != "patch" and not hasattr(VtkAxes, fn.__name__):
        setattr(VtkAxes, fn.__name__, draw)
    return draw


def figure(*args, **kwargs):
    return plt.figure(*args, **kwargs)


def subplot(*args, **kwargs):
    return plt.subplot(*args, projection=VtkAxes.name, **kwargs)


def hold(state="on", *, ax=None):
    ax = ax or gca()
    if state not in ("on", "off", True, False):
        raise ValueError("expected on or off")
    ax.holding = state in ("on", True)


def view(az=-37.5, el=30, *, ax=None):
    ax = ax or gca()
    if np.ndim(az) == 1:
        if len(az) == 2:
            az,el = az
        elif len(az) == 3:
            x,y,z = az
            az,el = np.degrees([np.arctan2(x,-y),np.arctan2(z,np.hypot(x,y))])
        else:
            raise ValueError("expected two view angles or an xyz view vector")
    elif az == 2:
        az,el = 0,90
    elif az == 3:
        az,el = -37.5,30
    ax.set_view(az, el)


def colorbar(handle=None, *, ax=None, **kwargs):
    ax = ax or (handle.axes if handle is not None else gca())
    if handle is None:
        handle = ax.handles[-1]
    return ax.figure.colorbar(handle, ax=ax, **kwargs)


def colormap(cmap, *, ax=None):
    ax = ax or gca()
    ax.default_cmap = _cmap(cmap)
    for h in ax.handles:
        h.set_cmap(ax.default_cmap)


def clim(limits=None, *, ax=None):
    ax = ax or gca()
    handles = [h for h in ax.handles if h._cdata_mapping == "scaled" and h.get_array() is not None]
    if limits is None:
        return ax.color_limits or (handles[-1].get_clim() if handles else (0.,1.))
    if _is(limits, "auto"):
        ax.color_limits = None
        for h in handles:
            h.autoscale()
        return
    lo, hi = limits
    if not np.isfinite((lo,hi)).all() or lo >= hi:
        raise ValueError("color limits must be two finite, increasing numbers")
    ax.color_limits = (lo,hi)
    for h in handles:
        h.set_clim(lo,hi)


caxis = clim


def alim(limits=None, *, ax=None):
    ax = ax or gca()
    if limits is None:
        return ax.alpha_limits
    lo, hi = limits
    if not np.isfinite((lo,hi)).all() or lo >= hi:
        raise ValueError("alpha limits must be two finite, increasing numbers")
    ax.alpha_limits = (lo,hi)
    for h in ax.handles:
        if isinstance(h,Graphic) and h._alpha_mapping == "scaled":
            h._refresh()


def text(x, y, z, label, *, ax=None, **kwargs):
    ax = ax or gca()
    return ax.text(x, y, z, label, **kwargs)


def axis(mode="auto", *, ax=None):
    ax = ax or gca()
    if _is(mode, "on", "off"):
        ax.set_axis_on() if mode.lower() == "on" else ax.set_axis_off()
    elif _is(mode, "auto", "tight", "equal"):
        ax.autoscale(True, axis="both", tight=mode.lower() == "tight")
        ax._limits_dirty = True
        ax.fit()
        ax.set_aspect("equal" if mode.lower() == "equal" else "auto")
    elif _is(mode, "vis3d"):
        ax.set_autoscale_on(False)
    else:
        bounds = np.asarray(mode, dtype=float)
        if bounds.shape == (8,):
            clim(bounds[6:], ax=ax)
            bounds = bounds[:6]
        if bounds.shape != (6,) or not np.all(bounds[::2] < bounds[1::2]):
            raise ValueError("expected [xmin,xmax,ymin,ymax,zmin,zmax]")
        for setter, limits in zip((ax.set_xlim, ax.set_ylim, ax.set_zlim), bounds.reshape(3,2)):
            setter(limits)
    ax.stale = True


def shading(mode="interp", *, ax=None):
    if mode not in ("flat", "interp", "faceted"):
        raise ValueError("expected flat, interp or faceted")
    for h in (ax or gca()).handles:
        if not isinstance(h,Graphic):
            continue
        h.face = "flat" if mode == "faceted" else mode
        h.actor.GetProperty().SetEdgeVisibility(mode == "faceted")
        h._refresh()


def lighting(mode="gouraud", *, ax=None):
    if mode not in ("none", "flat", "gouraud", "phong"):
        raise ValueError("unknown lighting model")
    for h in (ax or gca()).handles:
        if isinstance(h,Graphic):
            h.set_lighting(mode)


def camlight(az=0, el=0, *, ax=None):
    ax = ax or gca()
    light = vtk.vtkLight()
    light.SetLightTypeToCameraLight()
    if _is(az, "headlight"):
        light.SetLightTypeToHeadlight()
    else:
        if _is(az, "right", "left"):
            az, el = (30 if az == "right" else -30), 30
        light.SetDirectionAngle(float(el), float(az))
    ax.renderer.AddLight(light)
    return light


def light(position=(1.,0.,1.), *, color="white", style="infinite", ax=None):
    """Add a positional or directional world-space light."""
    ax = ax or gca()
    if style not in ("infinite","local"):
        raise ValueError("light style must be infinite or local")
    source = vtk.vtkLight()
    source.SetLightTypeToSceneLight()
    source.SetPosition(*position)
    source.SetFocalPoint(0,0,0)
    source.SetColor(to_rgb(ax._series_color(color)))
    source.SetPositional(style == "local")
    ax.renderer.AddLight(source)
    ax.stale = True
    return source


def lightangle(az, el, *, ax=None, **kwargs):
    a,e = np.deg2rad((az,el))
    return light((np.sin(a)*np.cos(e),-np.cos(a)*np.cos(e),np.sin(e)),ax=ax,**kwargs)


def camproj(mode=None, *, ax=None):
    ax = ax or gca()
    if mode is None:
        return "orthographic" if np.isinf(ax._focal_length) else "perspective"
    values = {"orthographic":"ortho","perspective":"persp","ortho":"ortho","persp":"persp"}
    ax.set_proj_type(values[mode])


def savefig(*args, **kwargs):
    return plt.gcf().savefig(*args, **kwargs)


def close(fig=None):
    fig = plt.gcf() if fig is None else fig
    figures = [plt.figure(n) for n in plt.get_fignums()] if fig == "all" else [fig]
    for f in figures:
        if isinstance(f, (int, str)):
            f = plt.figure(f)
        for a in f.axes:
            if isinstance(a, VtkAxes):
                a._close()
        plt.close(f)


show = plt.show


def title(label, *, ax=None, **kwargs):
    return (ax or gca()).set_title(label, **kwargs)


def xlabel(label, *, ax=None, **kwargs):
    return (ax or gca()).set_xlabel(label, **kwargs)


def ylabel(label, *, ax=None, **kwargs):
    return (ax or gca()).set_ylabel(label, **kwargs)


def zlabel(label, *, ax=None, **kwargs):
    return (ax or gca()).set_zlabel(label, **kwargs)


def grid(state="on", *, ax=None):
    ax = ax or gca()
    ax.grid(state in ("on", True))
    ax.stale = True


def hidden(state="on", *, ax=None):
    ax = ax or gca()
    ax.renderer.SetUseHiddenLineRemoval(state in ("on", True))
    ax.stale = True


def pbaspect(ratios, *, ax=None):
    (ax or gca()).set_plot_box_aspect(ratios)


def daspect(ratios, *, ax=None):
    ax = ax or gca()
    a = np.asarray(ratios,dtype=float)
    if a.shape != (3,) or not np.all(np.isfinite(a) & (a>0)):
        raise ValueError("data aspect ratio requires three positive finite values")
    spans = np.abs(np.diff(np.reshape(ax.get_w_lims(),(3,2)),axis=1).ravel())
    ax.set_box_aspect(spans/a)


def drawnow(*, ax=None):
    canvas = (ax or gca()).figure.canvas
    canvas.draw()
    canvas.flush_events()


def set(handle, *args, **kwargs):
    """Apply graphics property names or Python artist setters to a plot handle."""
    if len(args) % 2:
        raise TypeError("expected property name/value pairs")
    aliases = {"cdata":"cdata", "lighting":"lighting"}
    for name,value in {**dict(zip(args[::2],args[1::2])),**kwargs}.items():
        attr = _property_name(name)
        setter = getattr(handle,"set_"+aliases.get(attr,attr),None)
        if setter is None:
            raise AttributeError(f"the plot has no writable property {name!r}")
        setter(not _is(value,"off") and bool(value) if attr=="visible" else value)
    return handle


def material(style="dull", *, ax=None):
    presets = {"dull":(.3,.8,0.,10.), "shiny":(.3,.6,.9,20.), "metal":(.3,.3,1.,25.)}
    ka,kd,ks,power = presets[style] if isinstance(style,str) else style
    for h in (ax or gca()).handles:
        if not isinstance(h,Graphic):
            continue
        p = h.actor.GetProperty()
        p.SetAmbient(ka)
        p.SetDiffuse(kd)
        p.SetSpecular(ks)
        p.SetSpecularPower(power)
        h.axes.stale = True
