# Plotting API

Choose a method by the data you want to draw.

| Task | Methods |
| --- | --- |
| Surfaces and contours | [`plot_surface`](#plot_surface), [`plot_wireframe`](#plot_wireframe), [`plot_trisurf`](#plot_trisurf), [`contour`](#contour) |
| Lines, points, and charts | [`plot`](#plot), [`scatter`](#scatter), [`quiver`](#quiver), [`bar3d`](#bar3d), [`stem`](#stem) |

For volume and vector fields, use the [VTK reference](function_reference.md). For styling, cameras, and updates to existing plots, use [Scene and handles](scene.md).

## Run the examples

The examples below share this setup. Start each example with a fresh copy of it.

```python
import matplotlib.pyplot as plt
import numpy as np
import mpl3d_vtk

fig, ax = plt.subplots(subplot_kw={"projection": "vtk3d"})
t = np.linspace(-2, 2, 61)
x, y = np.meshgrid(t, t)
z = np.exp(x * np.sin(y))
```

## Common style options

Methods with `**style` accept the following keyword arguments. Each method also documents its own options.

| Option | Meaning |
| --- | --- |
| `color`, `facecolor`, `edgecolor` | A Matplotlib color name, hex color, or RGB tuple. `facecolor` overrides the fixed face color. `edgecolor="none"` hides polygon edges. Use `wireframe=True` to draw edges only. |
| `alpha`, `edge_alpha`, `vertex_alpha` | Overall opacity, edge opacity, or opacity broadcast across the associated color values. Use values from 0 to 1. With `association="cell"`, `vertex_alpha` is paired with face values. |
| `linewidth`, `linestyle` | Line width in output pixels and a style from `"-"`, `"--"`, `":"`, `"-."`, or `"none"`. Line appearance depends on the rendering backend. |
| `cmap`, `norm`, `vmin`, `vmax` | Scalar color mapping. Accepts Matplotlib colormaps and normalization objects. `cmap` also accepts an RGB(A) table. A fixed color takes precedence on the geometry. |
| `lighting`, `ambient`, `diffuse`, `specular`, `specular_power` | Lighting can be a boolean or `"flat"`, `"gouraud"`, or `"phong"`. The other arguments control the material's ambient, diffuse, and specular response. |
| `label`, `visible` | Legend label and visibility. |

## Surfaces and contours

### `plot_surface`

```text
ax.plot_surface(x, y, z, *, values=None, rcount=None, ccount=None,
                rstride=None, cstride=None, facecolors=None, shade=None, **style)
```

Plot a regular height grid. Use one-dimensional X and Y coordinate vectors or broadcastable grids with a two-dimensional `z` array. The resulting grid must have at least two rows and columns. Cells with nonfinite vertex coordinates are skipped.

`values` accepts one scalar per vertex or an array shaped `(ny, nx, 3)` or `(ny, nx, 4)` for RGB(A). `facecolors` is an alternative name for this input. With a colormap and no explicit values, the surface is colored by height. Unless sampling is requested, all input points are kept. Use either a count of at least two or a positive stride per direction. Both modes retain the grid boundary. Set `shade=True` for lighting or choose an interpolation mode with `lighting`.

Returns a [`Graphic`](#graphic) that supports colorbars, `set_heights()`, and `set_values()`.

```python
surface = ax.plot_surface(t, t, z, cmap="viridis", vmin=0, vmax=8)
fig.colorbar(surface, ax=ax)
surface.set_heights(z + .2)
```

<img src="gallery/reference/plot_surface.png" width="460" alt="Exponential surface colored by its height, with a scalar colorbar">

### `plot_wireframe`

```text
ax.plot_wireframe(x, y, z, *, rcount=None, ccount=None, rstride=None, cstride=None, **style)
```

Draw a regular grid as lines. The coordinate arrays and sampling parameters follow [`plot_surface`](#plot_surface). Use `color` for a uniform line color or a `cmap` to map height to line color. Returns a `Graphic` with `set_heights()`.

```python
wireframe = ax.plot_wireframe(x, y, z, rstride=4, cstride=4, color="0.25", linewidth=1)
```

<img src="gallery/reference/plot_wireframe.png" width="460" alt="A sampled line mesh over the exponential height field">

### `plot_trisurf`

```text
ax.plot_trisurf(x, y=None, z=None, *, triangles=None,
                values=None, association="point", shade=None, **style)
```

Plot triangles from one-dimensional X and Y coordinates and Z heights. Provide zero-based `(n, 3)` triangle indices or let Matplotlib triangulate XY. You can also call `ax.plot_trisurf(triangulation, z, ...)` with a Matplotlib `Triangulation`. Its mask selects which faces are rendered.

Color `values` correspond to vertices by default or to retained faces with `association="cell"`. When a colormap is supplied without values, the handle colors by vertex height or mean face height. Returns a `Graphic`. Use [`plot_mesh`](function_reference.md#plot_mesh) for meshes with vertices at arbitrary XYZ positions.

```python
triangles = [[0, 1, 2], [1, 3, 2]]
surface = ax.plot_trisurf([0, 1, 0, 1], [0, 0, 1, 1], [0, 0, 1, 2],
                          triangles=triangles, cmap="plasma", edgecolor="0.25")
```

<img src="gallery/reference/plot_trisurf.png" width="460" alt="An explicit two-face triangulation colored by height">

### `contour`

```text
ax.contour(x, y, z, *, levels=10, offset=None, **style)
```

Extract contour lines from a gridded height field. Coordinates follow [`plot_surface`](#plot_surface). Set `levels` to a positive count or a sequence of values. By default, each line lies at its own height. Set `offset` to project all lines onto a single Z plane.

Returns a `Graphic` with `contour_levels` and VTK line connectivity in `data.GetLines()`.

```python
surface = ax.plot_surface(t, t, z, cmap="viridis", alpha=.65)
lines = ax.contour(t, t, z, levels=[1, 2, 4], offset=0, color="0.2")
```

<img src="gallery/reference/contour.png" width="460" alt="A transparent surface with three contour levels projected below it">

## Lines, points, and charts

### `plot`

```text
ax.plot(x, y, z=0, *, zdir="z", color=None, linestyle="-", marker=None, markersize=6, **style)
```

Draw one or more 3D polylines. Coordinates broadcast, and columns of 2D inputs can represent separate lines. Nonfinite vertices split a line into segments. A scalar `z` sets a common height. Use `zdir="x"` or `"y"` to place the third coordinate on another axis. Optional markers use `marker` and `markersize`.

Returns a list of `Graphic` objects. Each line and its optional markers occupy separate handles.

```python
theta = np.linspace(0, 4*np.pi, 140)
line, = ax.plot(np.cos(theta), np.sin(theta), np.linspace(-1, 1, len(theta)),
                color="tab:blue", linewidth=2, label="helix")
ax.legend()
```

<img src="gallery/reference/plot.png" width="460" alt="A blue three-dimensional helix with a legend">

### `scatter`

```text
ax.scatter(x, y, z=0, *, s=20, c=None, zdir="z", marker="o", filled=True, **style)
```

Plot markers at broadcastable coordinates. Nonfinite coordinates are omitted. Supply a nonnegative marker area `s` as a scalar or per-point array. `c` accepts a color, per-point scalar values, or RGB(A) colors. If no color is supplied, scatter uses the current Matplotlib color cycle.

Common marker shapes include circles, squares, diamonds, triangles, and crosses. Equal-size circles use screen-space markers. Other shapes or varying sizes use camera-facing geometry in the scene. Returns a `Graphic`. Add a colorbar when `c` contains scalar values.

```python
theta = np.linspace(0, 4*np.pi, 56)
heights = np.linspace(-1, 1, len(theta))
points = ax.scatter(np.cos(theta), np.sin(theta), heights, s=24, c=heights, cmap="viridis")
fig.colorbar(points, ax=ax)
```

<img src="gallery/reference/scatter.png" width="460" alt="Points on a helix colored by their individual heights">

### `quiver`

```text
ax.quiver(x, y, z, u, v, w, *, length=1., normalize=False,
          arrow_length_ratio=.2, show_heads=True, **style)
```

Draw vectors `(u, v, w)` at positions `(x, y, z)`. All six arrays broadcast together. `length` multiplies the vector magnitudes. `normalize=True` assigns a common length to all nonzero vectors. `arrow_length_ratio` is the fraction of the arrow occupied by its head, between 0 and 1. `show_heads=False` draws shafts only.

Returns a `Graphic` for the instanced arrows. Set `cmap` to color by the scaled vector magnitude.

```python
a, b = np.meshgrid(np.linspace(-1, 1, 5), np.linspace(-1, 1, 5))
arrows = ax.quiver(a, b, 0, -b, a, .35, length=.32, color="tab:orange")
ax.set(zlim=(-.2, .65))
ax.set_box_aspect((1, 1, .55))
```

<img src="gallery/reference/quiver.png" width="460" alt="An array of arrows showing the directions of a swirling vector field">

### `bar3d`

```text
ax.bar3d(x, y, z, dx, dy, dz, *, shade=True, **style)
```

Draw cuboids anchored at `(x, y, z)` with width `dx`, depth `dy`, and Z height `dz`. All inputs broadcast together. `shade` controls lighting. A colormap uses the top Z coordinate of each bar. Returns one `Graphic` for all bars.

```python
bars = ax.bar3d([0, 1, 2], [0, .5, 1], 0, .65, .65, [2, 5, 3], cmap="plasma")
ax.set_box_aspect((2.6, 1.65, 3))
```

<img src="gallery/reference/bar3d.png" width="460" alt="Three cuboid bars colored according to their heights">

### `stem`

```text
ax.stem(x, y, z, *, bottom=0, marker="o", markersize=6, **style)
```

Draw vertical lines from `bottom` to each sample. Positions and heights broadcast together. Returns `(stems, markers)` when markers are enabled or a single `Graphic` when `marker=None`. Removing the stems also removes their markers.

```python
stems, markers = ax.stem(t[::8], np.sin(t[::8]), np.cos(t[::8]),
                        bottom=-1, color="tab:green")
```

<img src="gallery/reference/stem.png" width="460" alt="Markers at the ends of vertical lines from a common baseline">

## VtkAxes

Create a [`VtkAxes`](scene.md#vtkaxes) and look up its scene controls.

## Axes controls

See [Axes controls](scene.md#axes-controls) for projection settings, antialiasing, and export to an RGBA array. The aliases `plot3D`, `scatter3D`, `quiver3D`, and `contour3D` use the same methods and figures as their lowercase names above.

## Graphic

See [Graphic handles](scene.md#graphic) for geometry properties and updates to existing plots.

## Migrating from older versions

Use Matplotlib for figure operations and call plotting methods on a `vtk3d` axes. Ordinary Python keyword arguments control style and slicing.

| Older call | Current call |
| --- | --- |
| `m.figure()`, `m.subplot()`, `m.savefig()` | `plt.figure()`, `fig.add_subplot(..., projection="vtk3d")`, `fig.savefig(...)` |
| `m.surf(ax, x, y, z, FaceAlpha=.5)` | `ax.plot_surface(x, y, z, alpha=.5)` |
| `m.trisurf(ax, triangles, x, y, z)` | `ax.plot_mesh(np.column_stack((x, y, z)), triangles)` |
| `m.isosurface(ax, x, y, z, volume, level)` | `ax.plot_isosurface(volume, coordinates=(x, y, z), level=level)` |
| `m.slice(ax, x, y, z, volume, [], [], [0])` | `ax.plot_volume_slices(volume, coordinates=(x, y, z), z=0)` |
| `m.hold("on")` | Add more plots to the same axes. |
| `handle.set_zdata(z)`, `handle.set_cdata(c)` | `handle.set_heights(z)`, `handle.set_values(c)` |
| MATLAB-style options or positional flags | Set keyword arguments such as `color="red"`, `alpha=.5`, and `lighting="gouraud"`. |
| `m.close(fig)` in an Agg batch job | Call `ax.remove()` for each VTK subplot, then `plt.close(fig)`. |
