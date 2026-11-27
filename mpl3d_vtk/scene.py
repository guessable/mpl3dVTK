"""Matplotlib handles for VTK geometry."""
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy
from matplotlib.artist import Artist
from matplotlib.cm import ScalarMappable
from matplotlib.colors import ListedColormap, to_rgb, to_rgba

from ._geometry import array, numeric, points, surface_cells, vertices


def _cmap(value):
    if isinstance(value, (tuple, list, np.ndarray)):
        return ListedColormap(value)
    return value


class Graphic(Artist, ScalarMappable):
    """A plotted VTK object and a mappable for Matplotlib colorbars."""

    def __init__(self, ax, data, values=None, *, association="point", mapper=None,
                 color=None, facecolor=None, edgecolor="none", linewidth=1,
                 linestyle="-", alpha=None, vertex_alpha=None, edge_alpha=None,
                 point_size=5, wireframe=False, lighting=False, ambient=.22,
                 diffuse=.78, specular=.12, specular_power=18, cmap=None,
                 norm=None, vmin=None, vmax=None, label=None, visible=True):
        if association not in ("point", "cell"):
            raise ValueError("association must be 'point' or 'cell'")
        Artist.__init__(self)
        ScalarMappable.__init__(self, norm=norm, cmap=_cmap(cmap))
        self.axes = ax
        self.data = data
        self.association = association
        self._geometry_key = None
        self._values = None
        self._vertex_alpha = vertex_alpha
        self.annotations = []
        self.actor = vtk.vtkActor()
        self.mapper = vtk.vtkPolyDataMapper() if mapper is None else mapper
        self._uses_mapper_bounds = mapper is not None
        self.mapper.SetInputData(data)
        self.actor.SetMapper(self.mapper)
        self._color = color
        self._facecolor = facecolor
        self._edgecolor = edgecolor
        self._wireframe = wireframe
        self._apply_colors()
        self.set_alpha(alpha)
        self.set_linewidth(linewidth)
        self.set_linestyle(linestyle)
        self.set_lighting(lighting)
        self.set_visible(visible)
        self.set_label(label)
        prop = self.actor.GetProperty()
        prop.SetPointSize(float(point_size))
        prop.SetAmbient(float(ambient))
        prop.SetDiffuse(float(diffuse))
        prop.SetSpecular(float(specular))
        prop.SetSpecularPower(float(specular_power))
        if edge_alpha is not None:
            prop.SetEdgeOpacity(float(edge_alpha))
        if values is None and data.GetPointData().GetScalars() is not None and association == "point":
            values = vtk_to_numpy(data.GetPointData().GetScalars())
        if values is not None:
            self._set_values(values)
        if vmin is not None or vmax is not None:
            self.set_clim(vmin, vmax)
        self.callbacks.connect("changed", self._refresh)
        self._refresh()
        ax.renderer.AddActor(self.actor)
        ax.add_artist(self)
        ax.handles.append(self)
        ax._limits_dirty = True
        ax.stale = True

    def _raw_bounds(self):
        # Glyph mapper bounds include the instanced geometry.
        if self._uses_mapper_bounds and self._geometry_key is None:
            return self.mapper.GetBounds()
        return self.data.GetBounds()

    def _render_bounds(self):
        if self._uses_mapper_bounds:
            return self.mapper.GetBounds()
        return self.mapper.GetInput().GetBounds() if self._geometry_key is not None else self.data.GetBounds()

    def _sync_geometry(self, transforms, nonlinear):
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
        self._apply_opacity()

    def _apply_opacity(self):
        alpha = self.get_alpha()
        self.actor.GetProperty().SetOpacity(self._color_alpha if alpha is None else alpha)

    def set_visible(self, visible):
        if self.axes is not None and bool(visible) != self.get_visible():
            self.axes._limits_dirty = True
        super().set_visible(visible)
        self.actor.SetVisibility(bool(visible))
        for companion in getattr(self, "_companions", ()):
            companion.set_visible(visible)
        for annotation in self.annotations:
            annotation.set_visible(visible)

    def _apply_colors(self):
        prop = self.actor.GetProperty()
        unfilled = isinstance(self._facecolor, str) and self._facecolor == "none"
        wireframe = self._wireframe or unfilled
        has_edge = self._edgecolor is not None and not (
            isinstance(self._edgecolor, str) and self._edgecolor == "none")
        prop.SetRepresentationToWireframe() if wireframe else prop.SetRepresentationToSurface()
        prop.SetEdgeVisibility(has_edge and not wireframe)
        if has_edge:
            prop.SetEdgeColor(to_rgb(self._edgecolor))
        self.constant_color = self._color if self._facecolor is None or unfilled else self._facecolor
        if wireframe and has_edge:
            self.constant_color = self._edgecolor
        rgba = to_rgba("white" if self.constant_color is None else self.constant_color)
        prop.SetColor(rgba[:3])
        self._color_alpha = rgba[3]
        self._apply_opacity()

    def set_color(self, color):
        self._color = color
        self._facecolor = None
        self._apply_colors()
        self._refresh()

    def set_facecolor(self, color):
        self._facecolor = color
        self._apply_colors()
        self._refresh()

    def set_edgecolor(self, color):
        self._edgecolor = color
        self._apply_colors()
        self._refresh()

    def set_linewidth(self, width):
        self.actor.GetProperty().SetLineWidth(float(width))
        self.stale = True

    def set_linestyle(self, style):
        patterns = {"-": 0xFFFF, "--": 0xF0F0, ":": 0xAAAA, "-.": 0xF4F4, "none": 0}
        if style not in patterns:
            raise ValueError("linestyle must be '-', '--', ':', '-.' or 'none'")
        self.actor.GetProperty().SetLineStipplePattern(patterns[style])
        self.stale = True

    def set_lighting(self, lighting):
        prop = self.actor.GetProperty()
        modes = {"flat": prop.SetInterpolationToFlat, "gouraud": prop.SetInterpolationToGouraud,
                 "phong": prop.SetInterpolationToPhong}
        mode = lighting if isinstance(lighting, str) else "phong"
        if mode not in modes:
            raise ValueError("lighting must be a boolean, 'flat', 'gouraud' or 'phong'")
        prop.SetLighting(bool(lighting))
        modes[mode]()
        if lighting and hasattr(self, "_surface_shape"):
            self._update_surface_normals()
        self.stale = True

    def _update_surface_normals(self):
        if not self.actor.GetProperty().GetLighting():
            return
        from .surfaces import _normals
        xyz = vertices(self.data).reshape(self._surface_shape + (3,))
        normals = _normals(xyz).reshape(-1, 3)
        normals[~np.isfinite(normals).all(axis=1)] = (0, 0, 1)
        self.data.GetPointData().SetNormals(array(normals, "normals"))

    def _value_count(self):
        if self.association == "point":
            return self.data.GetNumberOfPoints()
        return self.data.GetNumberOfCells()

    def _set_values(self, values):
        if values is None:
            self._values = None
        else:
            values = np.asanyarray(values)
            count = self._value_count()
            if values.size == count:
                self._values = numeric(values).reshape(count)
            elif values.ndim >= 2 and values.shape[-1] in (3, 4) and values.size == count * values.shape[-1]:
                self._values = np.asarray(values).reshape(count, values.shape[-1])
            else:
                raise ValueError(f"expected {count} scalars or RGB(A) colors")
        values = self._values
        ScalarMappable.set_array(self, values if values is not None and values.ndim == 1 else None)
        if values is not None and values.ndim == 1:
            self._values = self.get_array()

    def set_values(self, values):
        """Update scalar values or RGB(A) colors on the existing geometry."""
        self._set_values(values)
        self._refresh()
        return self

    def set_array(self, values):
        """Set the scalar array using the Matplotlib ScalarMappable interface."""
        if values is not None and np.size(values) != self._value_count():
            raise ValueError(f"expected {self._value_count()} scalar values")
        self.set_values(values)

    def _refresh(self, *_):
        values = self._values
        if (self.constant_color is not None or values is None) and self._vertex_alpha is None:
            self.mapper.ScalarVisibilityOff()
            self.stale = True
            return

        if self.constant_color is not None or values is None:
            color = self.constant_color if self.constant_color is not None else "white"
            rgba = np.broadcast_to(np.round(255 * np.array(to_rgba(color))).astype(np.uint8),
                                   (self._value_count(), 4))
        elif values.ndim == 1:
            rgba = self.to_rgba(values, bytes=True)
        elif values.dtype == np.uint8:
            rgba = values
        else:
            rgba = (np.clip(values, 0, 1) * 255).round().astype(np.uint8)

        if self._vertex_alpha is not None:
            alpha = np.broadcast_to(numeric(self._vertex_alpha).ravel(), (len(rgba),))
            rgba = np.column_stack((rgba[:, :3], np.nan_to_num(np.clip(alpha, 0, 1)) * 255)).astype(np.uint8)

        point_values = self.association == "point"
        attrs = self.data.GetPointData() if point_values else self.data.GetCellData()
        colors = attrs.GetArray("display_rgba")
        if colors is not None and (colors.GetNumberOfTuples(), colors.GetNumberOfComponents()) == rgba.shape:
            vtk_to_numpy(colors)[:] = rgba
            colors.Modified()
            attrs.Modified()
        else:
            attrs.AddArray(array(rgba, "display_rgba"))
            if point_values:
                self.mapper.SetScalarModeToUsePointFieldData()
            else:
                self.mapper.SetScalarModeToUseCellFieldData()
            self.mapper.SelectColorArray("display_rgba")
            self.mapper.SetColorModeToDirectScalars()
        self.mapper.ScalarVisibilityOn()
        self.stale = True

    @property
    def vertices(self):
        return vertices(self.data).copy()

    @property
    def faces(self):
        cells = self.data.GetPolys()
        count = cells.GetNumberOfCells()
        if not count:
            return np.empty((0, 3), dtype=int)
        ids = vtk_to_numpy(cells.GetConnectivityArray())
        cell_size = cells.IsHomogeneous()
        if cell_size >= 0:
            return ids.reshape(count, cell_size).copy()
        offsets = vtk_to_numpy(cells.GetOffsetsArray())
        return [ids[a:b].copy() for a,b in zip(offsets, offsets[1:])]

    def set_heights(self, z):
        """Update the heights of a gridded surface without replacing its points."""
        z = numeric(z)
        if z.shape != getattr(self, "_surface_shape", None):
            raise ValueError("heights must match the original surface grid")
        xyz = vertices(self.data)
        new_heights = z.ravel()
        all_finite = self._surface_xy_finite and np.isfinite(new_heights).all()
        if not all_finite:
            old_valid = np.isfinite(xyz).all(axis=1)
            new_valid = np.isfinite(xyz[:, :2]).all(axis=1) & np.isfinite(new_heights)
            if not np.array_equal(old_valid, new_valid):
                self.data.SetPolys(surface_cells(z.shape, new_valid))
        elif not self._surface_all_finite:
            self.data.SetPolys(surface_cells(z.shape))
        self._surface_all_finite = all_finite
        xyz[:, 2] = new_heights
        self.data.GetPoints().Modified()
        self._update_surface_normals()
        if self._color_tracks_height:
            self.set_values(z)
        if self.axes is not None:
            self.axes._limits_dirty = True
        self.stale = True
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
