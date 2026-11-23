"""VTK glyphs and streamline integration for Cartesian vector fields."""
from operator import index

import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy

from ._geometry import array, line_data, numeric, output, poly, sample, surface_poly, vertices, volume_arrays, volume_flat, volume_grid
from .scene import Graphic
from .volumes import _sample_rectilinear


def _xyz(values):
    return np.column_stack([a.ravel() for a in np.broadcast_arrays(*map(numeric, values))])


def _glyphs(ax, xyz, vectors, source, style, values=None):
    valid = np.isfinite(xyz).all(axis=1) & np.isfinite(vectors).all(axis=1)
    if not valid.all():
        xyz, vectors = xyz[valid], vectors[valid]
    speed = np.linalg.norm(vectors, axis=1)
    data = poly(xyz)
    data.GetPointData().SetVectors(array(vectors, "vectors"))
    data.GetPointData().AddArray(array(speed, "speed"))
    mapper = vtk.vtkGlyph3DMapper()
    mapper.SetSourceConnection(source.GetOutputPort())
    mapper.SetOrientationArray("vectors")
    mapper.SetScaleArray("speed")
    mapper.SetScaleModeToScaleByMagnitude()
    if values is None:
        values = speed
        if "color" not in style and "cmap" not in style and "facecolor" not in style:
            style["color"] = ax._get_lines.get_next_color()
    else:
        values = np.asarray(values)[valid]
    return Graphic(ax, data, values, mapper=mapper, **style)


def _quiver(ax, x, y, z, u, v, w, *, length=1., normalize=False,
            arrow_length_ratio=.2, show_heads=True, **style):
    if not np.isfinite(length) or length < 0:
        raise ValueError("length must be finite and nonnegative")
    if not 0 <= arrow_length_ratio <= 1:
        raise ValueError("arrow_length_ratio must be in [0, 1]")
    x, y, z, u, v, w = np.broadcast_arrays(*map(numeric, (x, y, z, u, v, w)))
    vectors = _xyz((u, v, w))
    if normalize:
        vectors /= np.maximum(np.linalg.norm(vectors, axis=1, keepdims=True), 1e-30)
    source = vtk.vtkArrowSource()
    source.SetTipLength(arrow_length_ratio if show_heads else 0)
    source.SetTipRadius(.08 if show_heads else 0)
    source.SetShaftRadius(.014)
    return _glyphs(ax, _xyz((x, y, z)), vectors * length, source, style)


def _field(vectors, coordinates):
    vectors = numeric(vectors)
    if vectors.ndim != 4 or vectors.shape[-1] != 3:
        raise ValueError("vectors must have shape (ny, nx, nz, 3)")
    coords, shape_reference = volume_arrays(vectors[..., 0], coordinates)
    data = volume_grid(coords, shape_reference, image=True, scalars=False)
    data.GetPointData().SetVectors(array(vectors.transpose(2, 0, 1, 3).reshape(-1, 3), "vectors"))
    return coords, data


def _point_array(points, name):
    points = np.atleast_2d(numeric(points))
    if points.ndim != 2 or points.shape[1] != 3 or not np.isfinite(points).all():
        raise ValueError(f"{name} must contain finite (x, y, z) points")
    return points


def plot_vector_samples(self, vectors, points, *, coordinates=None, color_values=None,
                        interpolation="linear", glyph="cone", length=1., **style):
    """Interpolate a vector field at points and draw cones or arrows there."""
    if glyph not in ("cone", "arrow"):
        raise ValueError("glyph must be 'cone' or 'arrow'")
    if interpolation not in ("linear", "nearest", "cubic"):
        raise ValueError("interpolation must be 'linear', 'nearest' or 'cubic'")
    if not np.isfinite(length) or length < 0:
        raise ValueError("length must be finite and nonnegative")
    points = _point_array(points, "points")
    vectors = numeric(vectors)
    coords, field = _field(vectors, coordinates)
    if color_values is not None:
        color_values = numeric(color_values)
        if color_values.shape != vectors.shape[:3]:
            raise ValueError("color_values must match the vector grid")
    if interpolation == "linear":
        if color_values is not None:
            field.GetPointData().AddArray(array(volume_flat(color_values), "colors"))
        sampled = sample(field, poly(points)).GetPointData()
        valid = vtk_to_numpy(sampled.GetArray("vtkValidPointMask")).astype(bool)
        points = points[valid]
        sampled_vectors = vtk_to_numpy(sampled.GetVectors())[valid]
        if color_values is not None:
            color_values = vtk_to_numpy(sampled.GetArray("colors"))[valid]
    else:
        sampled_vectors = np.column_stack([
            _sample_rectilinear(coords, component, points, interpolation)
            for component in np.moveaxis(vectors, -1, 0)
        ])
        if color_values is not None:
            color_values = _sample_rectilinear(coords, color_values, points, interpolation)
    source = vtk.vtkArrowSource() if glyph == "arrow" else vtk.vtkConeSource()
    if glyph == "cone":
        source.SetCenter(.5, 0, 0)
        source.SetDirection(1, 0, 0)
        source.SetRadius(.22)
        source.SetResolution(16)
    return _glyphs(self, points, sampled_vectors * length, source, style, color_values)


def _trace(field, seeds, step=.1, max_steps=10000, direction="forward"):
    if not np.isfinite(step) or step <= 0 or index(max_steps) < 1:
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
    if direction not in methods:
        raise ValueError("direction must be 'forward', 'backward' or 'both'")
    methods[direction]()
    return output(tracer, field)


def _paths(data):
    offsets = vtk_to_numpy(data.GetLines().GetOffsetsArray())
    ids = vtk_to_numpy(data.GetLines().GetConnectivityArray())
    xyz = vertices(data)
    return [xyz[ids[a:b]].copy() for a, b in zip(offsets, offsets[1:])]


def trace_streamlines(vectors, seeds, *, coordinates=None, step=.1, max_steps=10000,
                      direction="forward"):
    """Integrate a 3-D vector grid from seeds and return a list of (n, 3) paths."""
    _, field = _field(vectors, coordinates)
    return _paths(_trace(field, _point_array(seeds, "seeds"), step, max_steps, direction))


def _path_data(paths):
    if isinstance(paths, Graphic):
        return paths.data
    if isinstance(paths, np.ndarray) and paths.ndim == 2:
        paths = [paths]
    return line_data(paths)


def plot_streamlines(self, paths, **style):
    """Draw paths returned by trace_streamlines."""
    if "color" not in style:
        style["color"] = self._get_lines.get_next_color()
    return Graphic(self, _path_data(paths), **style)


def plot_streamtubes(self, paths, *, radius=None, radii=None, sides=20, **style):
    """Render paths as tubes with a uniform radius or one radius per vertex."""
    data = _path_data(paths)
    tube = vtk.vtkTubeFilter()
    if radius is None:
        radius = max(data.GetLength(), 1e-12) * .012
    if not np.isfinite(radius) or radius <= 0 or index(sides) < 3:
        raise ValueError("radius must be positive and sides must be at least 3")
    if radii is not None:
        radii = numeric(radii).ravel()
        if len(radii) != data.GetNumberOfPoints() or not np.isfinite(radii).all() or np.any(radii <= 0):
            raise ValueError("radii must contain one positive value per streamline vertex")
        styled = vtk.vtkPolyData()
        styled.ShallowCopy(data)
        styled.GetPointData().SetScalars(array(radii, "radii"))
        data = styled
        tube.SetVaryRadiusToVaryRadiusByAbsoluteScalar()
    tube.SetRadius(radius)
    tube.SetNumberOfSides(sides)
    tube.CappingOn()
    if "color" not in style and "cmap" not in style:
        style["color"] = self._get_lines.get_next_color()
    style.setdefault("lighting", True)
    return Graphic(self, output(tube, data), **style)


def plot_streamribbons(self, paths, *, width=None, twists=None, **style):
    """Render paths as strips. Optional twists are angles in radians per vertex."""
    data = _path_data(paths)
    width = max(data.GetLength(), 1e-12) * .03 if width is None else float(width)
    if not np.isfinite(width) or width <= 0:
        raise ValueError("width must be positive")
    paths = _paths(data)
    if twists is None:
        twists = [0] * len(paths)
    if len(twists) != len(paths):
        raise ValueError("twists must provide one sequence per path")
    meshes = vtk.vtkAppendPolyData()
    for path, twist in zip(paths, twists):
        tangent = np.gradient(path, axis=0)
        tangent /= np.maximum(np.linalg.norm(tangent, axis=1, keepdims=True), 1e-30)
        normal = np.cross(tangent, np.eye(3)[np.argmin(np.abs(tangent[0]))])
        normal /= np.maximum(np.linalg.norm(normal, axis=1, keepdims=True), 1e-30)
        theta = np.broadcast_to(numeric(twist), (len(path),))[:, None]
        normal = normal * np.cos(theta) + np.cross(tangent, normal) * np.sin(theta)
        strip = np.stack((path - normal * width / 2, path + normal * width / 2), axis=1)
        meshes.AddInputData(surface_poly(*np.moveaxis(strip, -1, 0)))
    if "color" not in style:
        style["color"] = self._get_lines.get_next_color()
    style.setdefault("lighting", True)
    return Graphic(self, output(meshes) if paths else poly(np.empty((0, 3))), **style)
