"""Native Matplotlib 3D axes with a transparent VTK geometry layer."""
from itertools import product
from operator import index

import numpy as np
from PIL import Image
import vtk
from vtk.util.numpy_support import vtk_to_numpy
import matplotlib as mpl
from matplotlib.artist import Artist, allow_rasterization
from matplotlib.projections import register_projection
from matplotlib.transforms import Bbox
from mpl_toolkits.mplot3d import Axes3D

from ._projected_ticks import apply_repository_axes


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

    def __init__(self, *args, antialiasing=2, axes_style="my-mpl-style", **kwargs):
        if axes_style not in ("my-mpl-style", "matplotlib"):
            raise ValueError("axes_style must be 'my-mpl-style' or 'matplotlib'")
        self._axes_style = axes_style
        self._default_equal_aspect = False
        self._style_aspect_limits = None
        repository_style = axes_style == "my-mpl-style"
        use_default_aspect = "aspect" not in kwargs and kwargs.get("box_aspect") is None
        if repository_style:
            kwargs.setdefault("elev", 30)
            kwargs.setdefault("azim", -127.5)
            kwargs.setdefault("proj_type", "persp" if kwargs.get("focal_length") is not None
                              and np.isfinite(kwargs["focal_length"]) else "ortho")
        self._antialiasing = _sampling_factor(antialiasing)
        super().__init__(*args, **kwargs)
        if repository_style:
            apply_repository_axes(self)
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
        self.default_cmap = mpl.rcParams["image.cmap"]
        self.color_limits = None
        self.alpha_limits = (0.,1.)
        self.holding = False
        self._inside_plot = False
        self._limits_dirty = False
        self._viewport = _Viewport(self)
        self.add_artist(self._viewport)
        self._close_id = self.figure.canvas.mpl_connect("close_event", self._close)
        self._viewport_key = None
        self._viewport_frame = None

    @property
    def _azimuth(self):
        return self.azim+90

    @property
    def _elevation(self):
        return self.elev

    def set_view(self, az, el):
        self.view_init(elev=el, azim=az-90)

    def set_plot_box_aspect(self, ratios):
        self.set_box_aspect(ratios)

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
        for handle in self.handles.copy():
            handle.remove()

    def clear(self):
        if hasattr(self, "handles"):
            self.clear_scene()
        super().clear()
        if hasattr(self, "_viewport"):
            self.default_cmap = mpl.rcParams["image.cmap"]
            self.color_limits = None
            self.alpha_limits = (0.,1.)
            self.renderer.RemoveAllLights()
            self.add_artist(self._viewport)
            if self._axes_style == "my-mpl-style":
                apply_repository_axes(self)

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
            records = [h.raw_bounds() for h in self.handles]
            records = [r for r in records if r[0] <= r[1] and np.isfinite(r).all()]
            if records:
                data = np.asarray(records).reshape(-1,3,2)
                bounds = np.stack((data[:,:,0].min(axis=0),data[:,:,1].max(axis=0)),axis=1)
                self.auto_scale_xyz(*bounds, had_data=False)
        self._limits_dirty = False

    def draw(self, renderer):
        from .charts import AnimatedLine
        for handle in self.handles:
            if isinstance(handle, AnimatedLine):
                handle._flush()
        if self._limits_dirty:
            self.fit()
        self._fit_style_aspect()
        super().draw(renderer)

    def _sync_camera(self):
        # Matplotlib first projects data with get_proj(), then maps xy with
        # transData. OpenGL instead takes clip coordinates in [-w,w].
        limits = np.array(self.get_w_lims()).reshape(3,2)
        scales = [axis.get_transform() for axis in (self.xaxis,self.yaxis,self.zaxis)]
        nonlinear = tuple(axis.get_scale() != "linear" for axis in (self.xaxis,self.yaxis,self.zaxis))
        for i in range(3):
            if nonlinear[i]:
                limits[i] = scales[i].transform(limits[i])
        for h in self.handles:
            h.sync_geometry(scales,nonlinear)
        box = self.bbox
        affine = self.transData.get_affine().get_matrix()
        ndc = np.array([[2/box.width,0,-1-2*box.x0/box.width],
                        [0,2/box.height,-1-2*box.y0/box.height], [0,0,1]])
        plane = ndc @ affine
        m = self.get_proj()
        combined = m.copy()
        combined[:2] = plane[:2] @ m[[0,1,3]]
        bounds = limits.copy()
        for h in self.handles:
            b = np.asarray(h.mapper.GetBounds()).reshape(3,2)
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

    def _frame_key(self, width, height):
        lights = tuple(light.GetMTime() for light in self.renderer.GetLights())
        return (width, height, self._antialiasing, tuple(self.get_proj().ravel()),
                tuple(self.transData.get_affine().get_matrix().ravel()),
                lights, self.renderer.GetMTime(),
                tuple((h.get_visible(), h.actor.GetMTime(), h.mapper.GetMTime(), h.data.GetMTime())
                      for h in self.handles))

    def _render_frame(self, width, height, factor):
        render_size = (width*factor, height*factor)
        self.window.SetSize(*render_size)
        self._sync_camera()

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
        key = self._frame_key(width, height)
        if key == self._viewport_key:
            return self._viewport_frame
        self._viewport_frame = self._render_frame(width, height, self._antialiasing)
        self._viewport_key = self._frame_key(width, height)
        return self._viewport_frame

    def _close(self, event=None):
        self.window.Finalize()
        self._pixel_buffer.Initialize()
        self._viewport_key = None
        self._viewport_frame = None

    def remove(self):
        self.figure.canvas.mpl_disconnect(self._close_id)
        self._close()
        super().remove()

    def _add_plot(self, fn, *args, **kwargs):
        # Axes methods follow Matplotlib's additive semantics.
        holding = self.holding
        self.holding = True
        try:
            return fn(self,*args,**kwargs)
        finally:
            self.holding = holding

    def get_legend_handles_labels(self, legend_handler_map=None):
        from matplotlib.lines import Line2D
        handles, labels = super().get_legend_handles_labels(legend_handler_map)
        for h in self.handles:
            label = h.get_label()
            if not label or label.startswith("_"):
                continue
            color = h.constant_color if h.constant_color is not None else h.get_cmap()(.5)
            prop = h.actor.GetProperty()
            is_point = bool(h.data.GetNumberOfVerts())
            handles.append(Line2D([],[],color=color,alpha=prop.GetOpacity(),
                                  linewidth=prop.GetLineWidth(),label=label,
                                  marker="o" if is_point else None,
                                  linestyle="none" if is_point else "-"))
            labels.append(label)
        return handles,labels

    def legend(self, *args, **kwargs):
        if not args and "handles" not in kwargs and "labels" not in kwargs:
            args = self.get_legend_handles_labels(kwargs.get("handler_map"))
        return super().legend(*args, **kwargs)

    @staticmethod
    def _sample_grid(X, Y, Z, rcount, ccount, rstride, cstride):
        from ._geometry import numeric
        xyz = np.broadcast_arrays(*map(numeric, (X,Y,Z)))
        if xyz[0].ndim != 2:
            raise ValueError("surface arrays must be two-dimensional")
        cuts = []
        for n,count,stride in zip(xyz[0].shape,(rcount,ccount),(rstride,cstride)):
            if count is not None and stride is not None:
                raise ValueError("choose a count or stride per dimension")
            if any(v is not None and (int(v) != v or v <= 0) for v in (count,stride)):
                raise ValueError("sample counts and strides must be positive integers")
            step = int(stride or (np.ceil(n/count) if count else 1))
            cuts.append(np.unique(np.r_[np.arange(0,n,step),n-1]))
        return xyz, np.ix_(*cuts)

    def plot_surface(self, X, Y, Z, *, rcount=None, ccount=None, rstride=None,
                     cstride=None, facecolors=None, shade=None, **kwargs):
        from .surfaces import surf
        xyz, index = self._sample_grid(X,Y,Z,rcount,ccount,rstride,cstride)
        args = [a[index] for a in xyz]
        if facecolors is not None:
            args.append(np.asarray(facecolors)[index])
        if facecolors is None and "cmap" not in kwargs:
            kwargs.setdefault("color","C0")
        kwargs.setdefault("lighting",shade if shade is not None else "cmap" not in kwargs)
        return self._add_plot(surf,*args,**{"facecolor":"interp","edgecolor":"none",**kwargs})

    def plot_wireframe(self,X,Y,Z,*,rcount=None,ccount=None,rstride=None,cstride=None,**kwargs):
        from .surfaces import mesh
        xyz, index = self._sample_grid(X,Y,Z,rcount,ccount,rstride,cstride)
        return self._add_plot(mesh,*(a[index] for a in xyz),**kwargs)

    def plot(self,xs,ys,*args,zs=0,zdir="z",**kwargs):
        from .charts import plot3
        if args and not isinstance(args[0],str):
            zs,args = args[0],args[1:]
        x,y,z = self._oriented(xs,ys,zs,zdir)
        result = self._add_plot(plot3,x,y,z,*args,**kwargs)
        return result if isinstance(result,list) else [result]
    plot3D = plot

    @staticmethod
    def _oriented(x,y,z,direction):
        return {"z":(x,y,z),"x":(z,x,y),"y":(x,z,y)}[direction]

    def scatter(self,xs,ys,zs=0,zdir="z",s=20,c=None,**kwargs):
        from .charts import scatter3
        return self._add_plot(scatter3,*self._oriented(xs,ys,zs,zdir),s,c,**kwargs)
    scatter3D = scatter

    def plot_trisurf(self,*args,**kwargs):
        from matplotlib.tri import Triangulation
        from .surfaces import trisurf
        tri,args,kwargs = Triangulation.get_from_args_and_kwargs(*args,**kwargs)
        z = args[0] if args else kwargs.pop("Z")
        return self._add_plot(trisurf,tri.get_masked_triangles(),tri.x,tri.y,z,
                              **{"edgecolor":"none",**kwargs})

    def quiver(self,x,y,z,u,v,w,*,length=1.,normalize=False,**kwargs):
        from .vectors import quiver3
        vec = np.array(np.broadcast_arrays(u,v,w),dtype=float)
        if normalize:
            vec /= np.maximum(np.linalg.norm(vec,axis=0),1e-30)
        return self._add_plot(quiver3,x,y,z,*(vec*length),0,**kwargs)
    quiver3D = quiver

    def contour(self,*args,**kwargs):
        from .surfaces import contour3
        return self._add_plot(contour3,*args,**kwargs)
    contour3D = contour

    def bar3d(self,x,y,z,dx,dy,dz,**kwargs):
        from .charts import _bars
        x,y,z,dx,dy,dz = np.broadcast_arrays(x,y,z,dx,dy,dz)
        handle = _bars(self,x+dx/2,y+dy/2,z,z+dz,dx,dy,False,kwargs)
        self.fit()
        return handle

    def stem(self,x,y,z,*,bottom=0,**kwargs):
        from .charts import stem3
        return self._add_plot(stem3,x,y,z,baseline=bottom,**kwargs)
    stem3D = stem

    def add_collection3d(self, *args, **kwargs):
        raise NotImplementedError("Use the VTK plotting methods to add three-dimensional geometry.")


register_projection(VtkAxes)
