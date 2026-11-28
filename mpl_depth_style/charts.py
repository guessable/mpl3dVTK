"""Cartesian lines and markers for VtkAxes."""
import numpy as np
import vtk
from matplotlib.colors import is_color_like, to_rgba_array

from ._geometry import array, cells, coordinate_mesh, line_data, numeric, sequential_ids
from .scene import Graphic


def _columns(x, y, z):
    a = [np.squeeze(numeric(v)) for v in (x, y, z)]
    if any(v.ndim > 2 for v in a):
        raise ValueError("line coordinates must be scalars, vectors, or matrices")
    matrix = next((v for v in a if v.ndim == 2), None)
    if matrix is not None:
        lengths = {v.size for v in a if v.ndim == 1 and v.size > 1}
        if matrix.shape[0] not in lengths and matrix.shape[1] in lengths:
            a = [v.T if v.ndim == 2 else v for v in a]
        a = [v[:,None] if v.ndim == 1 else v for v in a]
    a = np.broadcast_arrays(*a)
    return zip(*(np.atleast_2d(v.T) for v in a))


def _line(ax, x, y, z, *, color=None, linestyle="-", marker=None, markersize=6, **style):
    handles = []
    for path in _columns(x, y, z):
        series_color = ax._get_lines.get_next_color() if color is None else color
        if linestyle not in (None, "", "none", "None"):
            handles.append(Graphic(ax, line_data(*path), color=series_color, linestyle=linestyle, **style))
        if marker not in (None, "", "none", "None"):
            marker_style = {name: style[name] for name in ("alpha", "visible", "label") if name in style}
            if handles and linestyle not in (None, "", "none", "None"):
                marker_style.pop("label", None)
            handles.append(_scatter(ax, *path, s=markersize**2, c=series_color,
                                    marker=marker, **marker_style))
    return handles


def _scatter(ax, x, y, z, *, s=20, c=None, marker="o", filled=True, **kwargs):
    x, y, z = np.broadcast_arrays(*map(numeric, (x, y, z)))
    valid = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    all_finite = valid.all()
    count = x.size
    if isinstance(c, str) or (isinstance(c, tuple) and is_color_like(c)):
        kwargs["color"], c = c, None
    if c is not None:
        c = np.asanyarray(c)
        if c.dtype.kind in ("U", "S", "O"):
            c = to_rgba_array(c)
        if c.ndim >= 2 and c.shape[-1] in (3, 4) and c.size != count:
            c = c.reshape(-1, c.shape[-1])
            if len(c) == 1:
                c = np.broadcast_to(c, (count, c.shape[-1]))
        else:
            c = numeric(c).ravel()
        if len(c) != count:
            raise ValueError("c must provide one value or color per point")
        if not all_finite:
            c = c[valid.ravel()]
    else:
        if "color" not in kwargs:
            kwargs["color"] = ax._get_lines.get_next_color()
    sizes = np.asarray(s, dtype=float)
    if sizes.size == 0:
        sizes = np.array(36.)
    if not np.isfinite(sizes).all() or np.any(sizes < 0):
        raise ValueError("marker areas must be finite and nonnegative")
    sizes = sizes.ravel()
    if not all_finite:
        x, y, z = x[valid], y[valid], z[valid]
    if sizes.size != 1:
        sizes = np.broadcast_to(sizes, (count,))
        if not all_finite:
            sizes = sizes[valid.ravel()]
    data = coordinate_mesh(x, y, z)
    data.SetVerts(cells(sequential_ids(x.size).reshape(-1, 1)))
    if marker in ("o", ".") and (sizes.size <= 1 or np.all(sizes == sizes[0])):
        h = Graphic(ax, data, c, point_size=np.sqrt(sizes[0]) if x.size else 1, **kwargs)
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
    data.GetPointData().AddArray(array(np.sqrt(np.broadcast_to(sizes, (x.size,))), "diameter"))
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
