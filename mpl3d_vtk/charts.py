"""Cartesian line, marker and bar primitives for VtkAxes."""
from operator import index

import numpy as np
import vtk
from matplotlib.colors import is_color_like, to_rgba_array

from ._geometry import array, cells, line_data, numeric, poly
from .scene import Graphic
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


def _line(ax, x, y, z, *, color=None, linestyle="-", marker=None, markersize=6, **style):
    handles = []
    for path in _columns(x, y, z):
        series_color = ax._get_lines.get_next_color() if color is None else color
        if linestyle not in (None, "", "none", "None"):
            handles.append(Graphic(ax, line_data([path]), color=series_color, linestyle=linestyle, **style))
        if marker not in (None, "", "none", "None"):
            marker_style = {name: style[name] for name in ("alpha", "visible", "label") if name in style}
            if handles and linestyle not in (None, "", "none", "None"):
                marker_style.pop("label", None)
            handles.append(_scatter(ax, *path.T, s=markersize**2, c=series_color,
                                    marker=marker, **marker_style))
    return handles


def _scatter(ax, x, y, z, *, s=20, c=None, marker="o", filled=True, **kwargs):
    xyz = _xyz((x, y, z))
    valid = np.isfinite(xyz).all(axis=1)
    if isinstance(c, str) or (isinstance(c, tuple) and is_color_like(c)):
        kwargs["color"], c = c, None
    if c is not None:
        c = np.asanyarray(c)
        if c.dtype.kind in ("U", "S", "O"):
            c = to_rgba_array(c)
        if c.ndim >= 2 and c.shape[-1] in (3, 4) and c.size != len(xyz):
            c = c.reshape(-1, c.shape[-1])
            if len(c) == 1:
                c = np.broadcast_to(c, (len(xyz), c.shape[-1]))
        else:
            c = numeric(c).ravel()
        if len(c) != len(xyz):
            raise ValueError("c must provide one value or color per point")
        if not valid.all():
            c = c[valid]
    else:
        if "color" not in kwargs:
            kwargs["color"] = ax._get_lines.get_next_color()
    sizes = np.asarray(s, dtype=float)
    if sizes.size == 0:
        sizes = np.array(36.)
    if not np.isfinite(sizes).all() or np.any(sizes < 0):
        raise ValueError("marker areas must be finite and nonnegative")
    sizes = np.broadcast_to(sizes.ravel(), (len(xyz),))[valid]
    data = poly(xyz[valid])
    data.SetVerts(cells(np.arange(len(sizes)).reshape(-1,1)))
    if marker in ("o",".") and (not sizes.size or np.all(sizes == sizes[0])):
        h = Graphic(ax, data, c, point_size=np.sqrt(sizes[0]) if sizes.size else 1, **kwargs)
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



def _stem(ax, x, y, z, *, bottom=0, marker="o", markersize=6, color=None, **style):
    xyz = _xyz((x, y, z))
    baseline = xyz.copy()
    baseline[:, 2] = bottom
    stems = Graphic(ax, line_data(np.stack((baseline, xyz), axis=1)),
                    color=ax._get_lines.get_next_color() if color is None else color, **style)
    if marker in (None, "", "none", "None"):
        return stems
    markers = _scatter(ax, *xyz.T, s=markersize**2, c=stems.constant_color, marker=marker)
    stems._companions = [markers]
    stems.set_visible(stems.get_visible())
    return stems, markers


def _bars(ax, x, y, base, top, wx, wy, opts):
    corners = np.array([[0,0,0],[1,0,0],[1,1,0],[0,1,0],
                        [0,0,1],[1,0,1],[1,1,1],[0,1,1]])
    xx, yy, low, high, wx, wy = np.broadcast_arrays(x,y,base,top,wx,wy)
    valid = np.isfinite(xx+yy+low+high+wx+wy)
    starts = np.column_stack(((xx-wx/2)[valid], (yy-wy/2)[valid], low[valid]))
    spans = np.column_stack((wx[valid], wy[valid], (high-low)[valid]))
    xyz = (starts[:,None,:] + spans[:,None,:]*corners).reshape(-1,3)
    sides = np.array([[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]])
    faces = (8*np.arange(len(starts))[:,None,None]+sides).reshape(-1,4)
    return Graphic(ax, poly(xyz, faces), np.repeat(high[valid],6), association="cell",
                   **{"edgecolor":"black", **opts})


class _StreamingLine(Graphic):
    """A line that batches new points until the next draw."""

    def __init__(self, ax, max_points, **style):
        if max_points is not None:
            max_points = index(max_points)
            if max_points < 1:
                raise ValueError("max_points must be positive")
        self._max_points = max_points
        self._history = np.empty((0, 3))
        self._pending = []
        if "color" not in style:
            style["color"] = ax._get_lines.get_next_color()
        super().__init__(ax, line_data([]), **style)

    def append(self, x, y, z=0):
        """Queue coordinates for the next draw."""
        self._pending.append(_xyz((x, y, z)))
        self.axes.stale = True

    def _flush(self):
        if not self._pending:
            return
        self._history = np.concatenate([self._history, *self._pending])
        if self._max_points is not None and len(self._history) > self._max_points:
            self._history = self._history[-self._max_points:].copy()
        self._pending.clear()
        self.data.ShallowCopy(line_data([self._history]))
        self.axes._limits_dirty = True

    def get_points(self):
        """Return copies of the current x, y and z coordinate arrays."""
        self._flush()
        return tuple(axis.copy() for axis in self._history.T)

    def clear_points(self):
        """Remove all queued and rendered points."""
        self._history = np.empty((0, 3))
        self._pending.clear()
        self.data.ShallowCopy(line_data([]))
        self.axes._limits_dirty = True
        self.axes.stale = True


def add_streaming_line(self, *, max_points=None, **style):
    """Add a line that can be updated with append(x, y, z)."""
    return _StreamingLine(self, max_points, **style)
