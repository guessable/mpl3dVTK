"""Native Matplotlib 3D axes with a transparent VTK geometry layer."""
from itertools import product
from operator import index

import numpy as np
from PIL import Image
import vtk
from vtk.util.numpy_support import vtk_to_numpy
from matplotlib.artist import Artist, allow_rasterization
from matplotlib.colors import to_rgb
from matplotlib.projections import register_projection
from matplotlib.tri import Triangulation
from matplotlib.transforms import Bbox
from mpl_toolkits.mplot3d import Axes3D

from . import charts, graphs, planes, spatial, surfaces, vectors, volumes
from ._geometry import surface_arrays
from ._projected_ticks import apply_axes_style


def _sampling_factor(value):
    try:
        factor = index(value)
    except TypeError as exc:
        raise ValueError("antialiasing must be an integer from 1 to 4") from exc
    if not 1 <= factor <= 4:
        raise ValueError("antialiasing must be an integer from 1 to 4")
    return factor


class _Viewport(Artist):
    def __init__(self, ax):
        super().__init__()
        self.scene = ax
        self.set_zorder(1)
        self.set_in_layout(False)

    @staticmethod
    def _nearest(start, stop, low, high, size):
        centers = np.arange(start, stop) + .5
        idx = np.floor((centers - low) * (size / (high - low))).astype(np.intp)
        np.clip(idx, 0, size-1, out=idx)
        return idx

    @allow_rasterization
    def draw(self, renderer):
        if self.get_visible() and any(h.get_visible() for h in self.scene.handles):
            self._draw_frame(renderer)
        self.stale = False

    def _draw_frame(self, renderer):
        box = self.scene.bbox
        clipped = Bbox.intersection(box, Bbox.from_bounds(0, 0, *renderer.get_canvas_width_height()))
        if clipped is None or box.width <= 0 or box.height <= 0:
            return
        mag = renderer.get_image_magnification()
        # Snap the visible extent to the same pixel convention as BboxImage.
        left, bottom, right, top = clipped.extents * mag
        x0 = int(np.floor(left+.5))
        y0 = int(np.ceil(bottom-.5-1e-8))
        x1 = int(np.floor(right+.5+1e-8))
        y1 = int(np.ceil(top-.5))
        if x0 >= x1 or y0 >= y1:
            return

        width, height = (max(1, round(v*mag)) for v in box.size)
        rgba = self.scene.pixels(width, height)
        # VTK has already downsampled its framebuffer to the output scale.
        # Only account for subpixel placement and clipping on the final canvas.
        columns = self._nearest(x0, x1, box.x0*mag, box.x1*mag, width)
        rows = self._nearest(y0, y1, box.y0*mag, box.y1*mag, height)
        extent = getattr(self.scene, "_viewport_extent", None)
        if extent is not None:
            left, bottom, right, top = extent
            first_col, last_col = np.searchsorted(columns, (left, right))
            first_row, last_row = np.searchsorted(rows, (bottom, top))
            if first_col >= last_col or first_row >= last_row:
                return
            columns = columns[first_col:last_col]
            rows = rows[first_row:last_row]
            x0 += first_col
            y0 += first_row
        if np.all(np.diff(columns) == 1) and np.all(np.diff(rows) == 1):
            rgba = rgba[rows[0]:rows[-1]+1, columns[0]:columns[-1]+1]
        else:
            rgba = rgba[rows[:, None], columns]
        gc = renderer.new_gc()
        try:
            self._set_gc_clip(gc)
            gc.set_alpha(1.)
            renderer.draw_image(gc, x0/mag, y0/mag, np.ascontiguousarray(rgba))
        finally:
            gc.restore()


class VtkAxes(Axes3D):
    """Matplotlib owns the axes. Only the three-dimensional data pass goes to VTK."""
    name = "vtk3d"

    def __init__(self, *args, antialiasing=2, **kwargs):
        self._default_equal_aspect = False
        self._style_aspect_limits = None
        use_default_aspect = "aspect" not in kwargs and kwargs.get("box_aspect") is None
        kwargs.setdefault("elev", 30)
        kwargs.setdefault("azim", -127.5)
        focal_length = kwargs.get("focal_length")
        kwargs.setdefault("proj_type", "persp" if focal_length is not None
                          and np.isfinite(focal_length) else "ortho")
        self._antialiasing = _sampling_factor(antialiasing)
        super().__init__(*args, **kwargs)
        apply_axes_style(self)
        if use_default_aspect:
            super().set_aspect("equal")
            self._default_equal_aspect = True
        self.renderer = vtk.vtkRenderer()
        self.window = vtk.vtkRenderWindow()
        self.window.SetOffScreenRendering(True)
        self.window.SwapBuffersOff()
        self.window.SetMultiSamples(0)
        self.window.SetAlphaBitPlanes(1)
        self.window.AddRenderer(self.renderer)
        self.renderer.SetBackground(0,0,0)
        self.renderer.SetBackgroundAlpha(0)
        self.renderer.UseDepthPeelingOn()
        self.renderer.SetMaximumNumberOfPeels(32)
        self.renderer.SetOcclusionRatio(0)
        self.capture = vtk.vtkWindowToImageFilter()
        self.capture.SetInput(self.window)
        self.capture.SetInputBufferTypeToRGBA()
        self.capture.ReadFrontBufferOff()
        self.capture.ShouldRerenderOff()
        self._pixel_buffer = vtk.vtkUnsignedCharArray()
        self.camera = self.renderer.GetActiveCamera()
        self.handles = []
        self._limits_dirty = False
        self._viewport = _Viewport(self)
        self.add_artist(self._viewport)
        self._close_id = self.figure.canvas.mpl_connect("close_event", self._close)
        self._viewport_key = None
        self._viewport_frame = None
        self._viewport_extent = None

    def set_box_aspect(self, aspect, *, zoom=1):
        # Explicit Matplotlib settings take precedence over the style default.
        super().set_box_aspect(aspect, zoom=zoom)
        self._default_equal_aspect = False

    def get_antialiasing(self):
        """Return the VTK render scale per output pixel dimension."""
        return self._antialiasing

    def set_antialiasing(self, factor):
        """Select 1× native rendering or 2× to 4× supersampling."""
        self._antialiasing = _sampling_factor(factor)
        self.stale = True

    def clear_scene(self):
        """Remove VTK plots while keeping axes settings and Matplotlib artists."""
        for handle in self.handles.copy():
            handle.remove()

    def clear(self):
        if hasattr(self, "handles"):
            self.clear_scene()
        super().clear()
        if hasattr(self, "_viewport"):
            self.renderer.RemoveAllLights()
            self.add_artist(self._viewport)
            apply_axes_style(self)

    def _fit_style_aspect(self):
        if self._default_equal_aspect and self.get_aspect() == "equal":
            self._unstale_viewLim()
            spans = tuple(np.ptp(np.asarray(self.get_w_lims()).reshape(3,2), axis=1))
            key = (spans, self._vertical_axis)
            if key != self._style_aspect_limits:
                super().set_box_aspect(spans)
                self._style_aspect_limits = key

    def fit(self):
        if self.handles:
            records = [h._raw_bounds() for h in self.handles]
            records = [r for r in records if r[0] <= r[1] and np.isfinite(r).all()]
            if records:
                data = np.asarray(records).reshape(-1,3,2)
                bounds = np.stack((data[:,:,0].min(axis=0),data[:,:,1].max(axis=0)),axis=1)
                self.auto_scale_xyz(*bounds, had_data=False)
        self._limits_dirty = False

    def draw(self, renderer):
        for handle in self.handles:
            if isinstance(handle, charts._StreamingLine):
                handle._flush()
        if self._limits_dirty:
            self.fit()
        self._fit_style_aspect()
        super().draw(renderer)

    def _sync_camera(self, projection, affine):
        # Matplotlib first projects data with get_proj(), then maps xy with
        # transData. OpenGL instead takes clip coordinates in [-w,w].
        limits = np.array(self.get_w_lims()).reshape(3,2)
        scales = [axis.get_transform() for axis in (self.xaxis,self.yaxis,self.zaxis)]
        nonlinear = tuple(axis.get_scale() != "linear" for axis in (self.xaxis,self.yaxis,self.zaxis))
        for i in range(3):
            if nonlinear[i]:
                limits[i] = scales[i].transform(limits[i])
        for h in self.handles:
            h._sync_geometry(scales,nonlinear)
        box = self.bbox
        ndc = np.array([[2/box.width,0,-1-2*box.x0/box.width],
                        [0,2/box.height,-1-2*box.y0/box.height], [0,0,1]])
        plane = ndc @ affine
        m = projection
        combined = m.copy()
        combined[:2] = plane[:2] @ m[[0,1,3]]
        bounds = limits.copy()
        for h in self.handles:
            b = np.asarray(h._render_bounds()).reshape(3,2)
            if b[0,0] <= b[0,1]:
                bounds[:,0] = np.minimum(bounds.min(axis=1), b[:,0])
                bounds[:,1] = np.maximum(bounds.max(axis=1), b[:,1])
        # Include the visible axis box so extreme zoom still has a valid
        # depth interval when data behind the eye is clipped by OpenGL.
        corners = np.array(list(product(*limits)) + list(product(*bounds)))
        clip = np.column_stack((corners,np.ones(len(corners)))) @ m.T
        front = clip[:,3] > 1e-9
        depth = clip[front,2]/clip[front,3]
        lo, hi = depth.min(), depth.max()
        scale = 1.8/max(hi-lo,1e-8)
        combined[2] = scale*(m[2] - .5*(lo+hi)*m[3])
        # A conventional physical camera gives lights a meaningful view frame.
        # Its view matrix is factored out of the explicit projection below.
        center = limits.mean(axis=1)
        right, up = m[0,:3], m[1,:3]
        back = np.cross(right,up)
        back /= max(np.linalg.norm(back),1e-30)
        up = up/max(np.linalg.norm(up),1e-30)
        billboard_right = np.cross(up,back)
        marker_matrix = np.eye(4)
        marker_matrix[:3,:3] = np.column_stack((billboard_right,up,back))
        for handle in self.handles:
            if hasattr(handle,"_marker_transform"):
                handle._marker_transform.SetMatrix(marker_matrix.ravel())
        distance = max(np.linalg.norm(np.ptp(limits,axis=1)), 1)
        self.camera.SetPosition(*(center+back*distance*2))
        self.camera.SetFocalPoint(*center)
        self.camera.SetViewUp(*up)
        modelview = self.camera.GetModelViewTransformMatrix()
        vm = np.array([[modelview.GetElement(i,j) for j in range(4)] for i in range(4)])
        explicit = vtk.vtkMatrix4x4()
        explicit.DeepCopy((combined @ np.linalg.inv(vm)).ravel())
        self.camera.SetExplicitProjectionTransformMatrix(explicit)
        self.camera.UseExplicitProjectionTransformMatrixOn()

    def _frame_key(self, width, height, projection, affine):
        lights = tuple(light.GetMTime() for light in self.renderer.GetLights())
        return (width, height, self._antialiasing, projection.tobytes(), affine.tobytes(),
                lights, self.renderer.GetMTime(),
                tuple((h.get_visible(), h.actor.GetMTime(), h.mapper.GetMTime(), h.data.GetMTime())
                      for h in self.handles))

    def _render_frame(self, width, height, factor, projection, affine):
        render_size = (width*factor, height*factor)
        self.window.SetSize(*render_size)
        self._sync_camera(projection, affine)

        # Lines and point sprites use framebuffer pixels. Scale them for the
        # high-resolution pass and restore their VTK properties afterwards.
        strokes = []
        if factor > 1:
            for handle in self.handles:
                actor = handle.actor
                if not handle.get_visible() or not actor.IsA("vtkActor"):
                    continue
                prop = actor.GetProperty()
                lines = (handle.data.GetNumberOfLines() or prop.GetEdgeVisibility()
                         or prop.GetRepresentation() == vtk.VTK_WIREFRAME
                         or hasattr(handle, "_marker_transform"))
                points = (handle.data.GetNumberOfVerts() or prop.GetRepresentation() == vtk.VTK_POINTS)
                width_px = prop.GetLineWidth() if lines else None
                size_px = prop.GetPointSize() if points else None
                if width_px is not None or size_px is not None:
                    strokes.append((prop, width_px, size_px))
        try:
            for prop, width_px, size_px in strokes:
                if width_px is not None:
                    prop.SetLineWidth(width_px*factor)
                if size_px is not None:
                    prop.SetPointSize(size_px*factor)
            self.window.Render()
            render_width, render_height = render_size
            if self.window.GetRGBACharPixelData(0, 0, render_width-1, render_height-1,
                                                0, self._pixel_buffer):
                buf = self._pixel_buffer
            else:
                self.capture.Modified()
                self.capture.Update()
                buf = self.capture.GetOutput().GetPointData().GetScalars()
            rgba = vtk_to_numpy(buf)
            # Filter VTK's premultiplied framebuffer before converting to the
            # straight alpha that Matplotlib expects. This avoids dark fringes.
            image = Image.frombuffer("RGBa", render_size, rgba, "raw", "RGBa", 0, 1)
            if factor > 1:
                image = image.reduce(factor)
            self._viewport_extent = image.getbbox() or (0, 0, 0, 0)
            # Matplotlib's Agg renderer requires a writable pixel buffer.
            return np.array(image.convert("RGBA"))
        finally:
            for prop, width_px, size_px in strokes:
                if width_px is not None:
                    prop.SetLineWidth(width_px)
                if size_px is not None:
                    prop.SetPointSize(size_px)

    def pixels(self, width, height):
        if self._limits_dirty:
            self.fit()
        projection = self.get_proj()
        affine = self.transData.get_affine().get_matrix()
        key = self._frame_key(width, height, projection, affine)
        if key == self._viewport_key:
            return self._viewport_frame
        self._viewport_frame = self._render_frame(width, height, self._antialiasing, projection, affine)
        self._viewport_key = self._frame_key(width, height, projection, affine)
        return self._viewport_frame

    def _close(self, event=None):
        self.window.Finalize()
        self._pixel_buffer.Initialize()
        self._viewport_key = None
        self._viewport_frame = None
        self._viewport_extent = None

    def remove(self):
        self.figure.canvas.mpl_disconnect(self._close_id)
        self._close()
        super().remove()

    def get_legend_handles_labels(self, legend_handler_map=None):
        from matplotlib.lines import Line2D
        handles, labels = super().get_legend_handles_labels(legend_handler_map)
        for h in self.handles:
            label = h.get_label()
            if not label or label.startswith("_"):
                continue
            color = getattr(h, "constant_color", None)
            color = h.get_cmap()(.5) if color is None else color
            prop = h.actor.GetProperty() if h.actor.IsA("vtkActor") else None
            is_point = prop is not None and bool(h.data.GetNumberOfVerts())
            handles.append(Line2D([],[],color=color,alpha=prop.GetOpacity() if prop else 1.,
                                  linewidth=prop.GetLineWidth() if prop else 1.,label=label,
                                  marker="o" if is_point else None,
                                  linestyle="none" if is_point else "-"))
            labels.append(label)
        return handles,labels

    def legend(self, *args, **kwargs):
        if not args and "handles" not in kwargs and "labels" not in kwargs:
            args = self.get_legend_handles_labels(kwargs.get("handler_map"))
        return super().legend(*args, **kwargs)

    def plot_surface(self, x, y, z, *, values=None, rcount=None, ccount=None,
                     rstride=None, cstride=None, facecolors=None, shade=None, **style):
        """Draw a surface from coordinate vectors or matching grids."""
        xyz = surface_arrays(x, y, z)
        if facecolors is not None:
            if values is not None:
                raise TypeError("supply either values or facecolors")
            values = facecolors
        if values is not None:
            values = np.asanyarray(values)
            if values.shape not in (xyz[2].shape, xyz[2].shape + (3,), xyz[2].shape + (4,)):
                raise ValueError("values must match the surface grid with optional RGB(A) channels")
        if any(option is not None for option in (rcount, ccount, rstride, cstride)):
            sample = self._grid_indices(xyz[2].shape, (rcount, ccount), (rstride, cstride))
            xyz = tuple(axis[sample] for axis in xyz)
            if values is not None:
                values = values[sample]
        if values is None and all(style.get(k) is None for k in ("cmap", "norm", "color", "facecolor")):
            style["color"] = self._get_lines.get_next_color()
        style.setdefault("lighting", shade if shade is not None else style.get("cmap") is None and values is None)
        return surfaces._surface(self, *xyz, values, style)

    @staticmethod
    def _grid_indices(shape, counts, strides):
        cuts = []
        for size, count, stride in zip(shape, counts, strides):
            if count is not None and stride is not None:
                raise ValueError("choose a count or stride per axis")
            if count is not None:
                count = index(count)
                if count < 2:
                    raise ValueError("sample counts must be at least two")
                indices = np.linspace(0, size - 1, min(count, size), dtype=np.intp)
            else:
                step = 1 if stride is None else index(stride)
                if step < 1:
                    raise ValueError("sample strides must be positive")
                indices = np.arange(0, size, step)
                if indices[-1] != size - 1:
                    indices = np.r_[indices, size - 1]
            cuts.append(indices)
        return np.ix_(*cuts)

    def plot_wireframe(self, x, y, z, *, rcount=None, ccount=None, rstride=None, cstride=None, **style):
        """Draw grid lines, optionally downsampling rows and columns."""
        xyz = surface_arrays(x, y, z)
        if any(option is not None for option in (rcount, ccount, rstride, cstride)):
            sample = self._grid_indices(xyz[2].shape, (rcount, ccount), (rstride, cstride))
            xyz = tuple(axis[sample] for axis in xyz)
        if "color" not in style and "cmap" not in style:
            style["color"] = self._get_lines.get_next_color()
        style["wireframe"] = True
        self.renderer.UseHiddenLineRemovalOn()
        return surfaces._surface(self, *xyz, None, style)

    def plot(self, x, y, z=0, *, zdir="z", color=None, linestyle="-", marker=None, markersize=6, **style):
        """Draw one or more lines from coordinate arrays."""
        return charts._line(self, *self._oriented(x, y, z, zdir), color=color, linestyle=linestyle,
                            marker=marker, markersize=markersize, **style)

    plot3D = plot

    @staticmethod
    def _oriented(x, y, z, direction):
        return {"z": (x, y, z), "x": (z, x, y), "y": (x, z, y)}[direction]

    def scatter(self, x, y, z=0, *, s=20, c=None, zdir="z", marker="o", filled=True, **style):
        """Draw 3-D markers with area s and an optional color or scalar array c."""
        return charts._scatter(self, *self._oriented(x, y, z, zdir), s=s, c=c, marker=marker,
                               filled=filled, **style)

    scatter3D = scatter

    def plot_trisurf(self, x, y=None, z=None, *, triangles=None, values=None,
                     association="point", shade=None, **style):
        """Draw a triangulation of x and y at heights z, with optional scalar values."""
        if isinstance(x, Triangulation):
            if triangles is not None or (y is not None and z is not None):
                raise TypeError("supply a Triangulation and one height array")
            triangulation, z = x, z if y is None else y
        else:
            triangulation = Triangulation(x, y, triangles)
        z = np.asarray(z)
        if z.shape != triangulation.x.shape:
            raise ValueError("z must have one height per triangulation vertex")
        faces = triangulation.get_masked_triangles()
        if values is None and style.get("cmap") is not None:
            values = z[faces].mean(axis=1) if association == "cell" else z
        style.setdefault("lighting", shade if shade is not None else style.get("cmap") is None)
        return self.plot_mesh(np.column_stack((triangulation.x, triangulation.y, z)), faces,
                              values=values, association=association, **style)

    def quiver(self, x, y, z, u, v, w, *, length=1., normalize=False, arrow_length_ratio=.2,
               show_heads=True, **style):
        """Draw vectors with proportional or normalized lengths."""
        return vectors._quiver(self, x, y, z, u, v, w, length=length, normalize=normalize,
                                arrow_length_ratio=arrow_length_ratio, show_heads=show_heads, **style)

    quiver3D = quiver

    def contour(self, x, y, z, *, levels=10, offset=None, **style):
        """Draw contours on a height grid or project them to offset along z."""
        return surfaces._contour(self, *surface_arrays(x, y, z), levels=levels, offset=offset, **style)

    contour3D = contour

    def bar3d(self, x, y, z, dx, dy, dz, *, shade=True, **style):
        """Draw bars from base coordinates and their widths, depths and heights."""
        x, y, z, dx, dy, dz = np.broadcast_arrays(x, y, z, dx, dy, dz)
        style.setdefault("lighting", shade)
        return charts._bars(self, x + dx/2, y + dy/2, z, z + dz, dx, dy, style)

    def stem(self, x, y, z, *, bottom=0, marker="o", markersize=6, **style):
        """Draw stems between a constant baseline and the supplied points."""
        return charts._stem(self, x, y, z, bottom=bottom, marker=marker, markersize=markersize, **style)

    def add_light(self, position, *, focal_point=(0., 0., 0.), color="white", positional=False):
        """Add a directional or positional VTK light in world coordinates."""
        source = vtk.vtkLight()
        source.SetLightTypeToSceneLight()
        source.SetPosition(*position)
        source.SetFocalPoint(*focal_point)
        source.SetColor(to_rgb(color))
        source.SetPositional(positional)
        self.renderer.AddLight(source)
        self.stale = True
        return source

    plot_mesh = surfaces.plot_mesh
    plot_isosurface = volumes.plot_isosurface
    plot_volume_slices = volumes.plot_volume_slices
    plot_slice_contours = volumes.plot_slice_contours
    plot_volume = spatial.plot_volume
    plot_point_cloud = spatial.plot_point_cloud
    plot_coordinate_frames = spatial.plot_coordinate_frames
    plot_alpha_shape = spatial.plot_alpha_shape
    plot_vector_samples = vectors.plot_vector_samples
    plot_streamlines = vectors.plot_streamlines
    plot_streamtubes = vectors.plot_streamtubes
    plot_streamribbons = vectors.plot_streamribbons
    plot_graph = graphs.plot_graph
    plot_image_plane = planes.plot_image_plane
    add_streaming_line = charts.add_streaming_line

    def add_collection3d(self, *args, **kwargs):
        raise NotImplementedError("Use the VTK plotting methods to add three-dimensional geometry.")


register_projection(VtkAxes)
