# Axes and graphics API

Import `mpl3d_vtk` to register `vtk3d`, then pass `projection="vtk3d"` to `Figure.add_subplot` or `plt.subplots`. Plotting calls on the same axes add to the scene. Standard Matplotlib methods control limits, labels, grid, view, annotations, legends, and colorbars.

- [Surface and line methods](#plot_surface)
- [Axes controls](#axes-controls)
- [Graphic handles](#graphic)
- [Migration](#migrating-from-older-versions)
- [VTK-specific plotting and geometry](function_reference.md)

## VtkAxes

`VtkAxes` extends Matplotlib's 3D axes. Pass `antialiasing` in `subplot_kw` to set the VTK render scale, from 1 to 4. The default is 2. The initial camera is orthographic with elevation 30° and azimuth −127.5°. Data units have equal lengths by default. Set an explicit `box_aspect` or pass `proj_type="persp"` to change these defaults.

The examples below share this setup. Use `ax.clear()` between examples to start a new scene.

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

## plot_surface

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

## plot_wireframe

```text
ax.plot_wireframe(x, y, z, *, rcount=None, ccount=None, rstride=None, cstride=None, **style)
```

Draw a regular grid as lines. The coordinate arrays and sampling parameters follow [`plot_surface`](#plot_surface). Use `color` for a uniform line color or a `cmap` to map height to line color. Returns a `Graphic` with `set_heights()`.

```python
wireframe = ax.plot_wireframe(x, y, z, rstride=4, cstride=4, color="0.25", linewidth=1)
```

## plot_trisurf

```text
ax.plot_trisurf(x, y=None, z=None, *, triangles=None,
                values=None, association="point", shade=None, **style)
```

Plot triangles from one-dimensional X and Y coordinates and Z heights. Provide zero-based `(n, 3)` triangle indices or let Matplotlib triangulate XY. You can also call `ax.plot_trisurf(triangulation, z, ...)` with a Matplotlib `Triangulation`. Its mask selects which faces are rendered.

Color `values` correspond to vertices by default or to retained faces with `association="cell"`. When a colormap is supplied without values, the handle colors by vertex height or mean face height. Returns a `Graphic`. Use [`plot_mesh`](function_reference.md#plot_mesh) for meshes with vertices at arbitrary XYZ positions.

```python
triangles = [[0, 1, 2], [1, 3, 2]]
surface = ax.plot_trisurf([0, 1, 0, 1], [0, 0, 1, 1], [0, 0, 1, 2],
                          triangles=triangles, cmap="plasma")
```

## plot

```text
ax.plot(x, y, z=0, *, zdir="z", color=None, linestyle="-", marker=None, markersize=6, **style)
```

Draw one or more 3D polylines. Coordinates broadcast, and columns of 2D inputs can represent separate lines. Nonfinite vertices split a line into segments. A scalar `z` sets a common height. Use `zdir="x"` or `"y"` to place the third coordinate on another axis. Optional markers use `marker` and `markersize`.

Returns a list of `Graphic` objects. Each line and its optional markers occupy separate handles.

```python
line, = ax.plot(np.cos(t), np.sin(t), t, color="tab:blue", linewidth=2, label="helix")
ax.legend()
```

## scatter

```text
ax.scatter(x, y, z=0, *, s=20, c=None, zdir="z", marker="o", filled=True, **style)
```

Plot markers at broadcastable coordinates. Nonfinite coordinates are omitted. Supply a nonnegative marker area `s` as a scalar or per-point array. `c` accepts a color, per-point scalar values, or RGB(A) colors. If no color is supplied, scatter uses the current Matplotlib color cycle.

Common marker shapes include circles, squares, diamonds, triangles, and crosses. Equal-size circles use screen-space markers. Other shapes or varying sizes use camera-facing geometry in the scene. Returns a `Graphic`. Add a colorbar when `c` contains scalar values.

```python
points = ax.scatter(np.cos(t), np.sin(t), t, s=24, c=t, cmap="viridis")
fig.colorbar(points, ax=ax)
```

## quiver

```text
ax.quiver(x, y, z, u, v, w, *, length=1., normalize=False,
          arrow_length_ratio=.2, show_heads=True, **style)
```

Draw vectors `(u, v, w)` at positions `(x, y, z)`. All six arrays broadcast together. `length` multiplies the vector magnitudes. `normalize=True` assigns a common length to all nonzero vectors. `arrow_length_ratio` is the fraction of the arrow occupied by its head, between 0 and 1. `show_heads=False` draws shafts only.

Returns a `Graphic` for the instanced arrows. Set `cmap` to color by the scaled vector magnitude.

```python
arrows = ax.quiver([0, 1], [0, 1], 0, [1, 0], [0, 1], 0, length=.4, color="tab:orange")
```

## contour

```text
ax.contour(x, y, z, *, levels=10, offset=None, **style)
```

Extract contour lines from a gridded height field. Coordinates follow [`plot_surface`](#plot_surface). Set `levels` to a positive count or a sequence of values. By default, each line lies at its own height. Set `offset` to project all lines onto a single Z plane.

Returns a `Graphic` with `contour_levels` and VTK line connectivity in `data.GetLines()`.

```python
surface = ax.plot_surface(t, t, z, cmap="viridis", alpha=.65)
lines = ax.contour(t, t, z, levels=[1, 2, 4], offset=0, color="0.2")
```

## bar3d

```text
ax.bar3d(x, y, z, dx, dy, dz, *, shade=True, **style)
```

Draw cuboids anchored at `(x, y, z)` with width `dx`, depth `dy`, and Z height `dz`. All inputs broadcast together. `shade` controls lighting. A colormap uses the top Z coordinate of each bar. Returns one `Graphic` for all bars.

```python
bars = ax.bar3d([0, 1, 2], 0, 0, .7, .6, [2, 5, 3], cmap="plasma")
```

## stem

```text
ax.stem(x, y, z, *, bottom=0, marker="o", markersize=6, **style)
```

Draw vertical lines from `bottom` to each sample. Positions and heights broadcast together. Returns `(stems, markers)` when markers are enabled or a single `Graphic` when `marker=None`. Removing the stems also removes their markers.

```python
stems, markers = ax.stem(t[::8], 0, np.cos(t[::8]), bottom=-1, color="tab:green")
```

## Axes controls

| Method | Parameters and result |
| --- | --- |
| `get_antialiasing()` | Return the offscreen render scale per image dimension. |
| `set_antialiasing(factor)` | Set an integer scale from 1 to 4. At 1, VTK renders at the final pixel size. At 2, it renders at twice the width and height before downsampling. |
| `set_box_aspect(aspect, *, zoom=1)` | Set the three display-box ratios and the camera zoom. Explicit ratios take precedence over the style default. |
| `fit()` | Recompute data bounds and apply the enabled autoscaling settings. The axes also update bounds on draw when geometry changes. |
| `clear_scene()` | Remove VTK plots and their dependent artists while keeping axes settings and independent Matplotlib artists. |
| `clear()` | Reset the subplot and reapply the `vtk3d` axes style. |
| `remove()` | Remove the subplot from its figure and release the VTK window. |
| `pixels(width, height)` | Render a `(height, width, 4)` RGBA array of `uint8` with its bottom row first. Copy the result before editing because it can be a cached frame. |
| `get_legend_handles_labels()` | Return two lists for the legend handles and labels. VTK plots contribute Matplotlib proxy artists. |
| `legend(*args, **kwargs)` | Create a Matplotlib legend with automatic or explicit handles and labels. |
| `add_collection3d(...)` | Raises `NotImplementedError` for native 3D collections. Use `plot_mesh` for polygons and `plot` for lines in the VTK scene. |

`plot3D`, `scatter3D`, `quiver3D`, and `contour3D` are Matplotlib aliases with the same arguments and return values as the methods above.

## Graphic

`Graphic` is a Matplotlib artist and scalar mappable. Plotting methods create it automatically. Advanced callers can wrap a VTK dataset with `Graphic(ax, data, values=None, *, association="point", mapper=None, **style)`. Set `association="cell"` to bind values to cells. Access `data`, `mapper`, and `actor` to use native VTK APIs. After modifying VTK arrays directly, call `Modified()` on the changed objects.

| Property or method | Result |
| --- | --- |
| `vertices`, `faces` | Copies of the XYZ coordinates and zero-based face indices. Equal-size faces return a 2D array. Mixed faces return a list of arrays. |
| `set_heights(z)` | Update a gridded surface in place. The new array must match the original shape. Changes to finite coordinates update face connectivity. Height-based colors follow the new heights. Explicit color values are retained. Returns the handle. |
| `set_values(values)` | Replace scalars or RGB(A) values for the existing vertices or cells and return the handle. `None` clears the values on ordinary meshes. An image plane uses this method to update its pixels without resizing. |
| `set_array(values)`, `get_array()` | Set or retrieve the Matplotlib scalar array used for normalization and colorbars. |
| `set_cmap(cmap)`, `set_clim(vmin, vmax)` | Update the colormap or range and refresh attached colorbars. |
| `set_color(color)`, `set_facecolor(color)`, `set_edgecolor(color)` | Set a fixed color, face color, or edge color. Use `set_edgecolor("none")` to hide edges. `set_facecolor(None)` restores the underlying color choice. |
| `set_alpha(alpha)`, `set_visible(visible)` | Set opacity from 0 to 1 or change visibility. `alpha=None` restores the default opacity. |
| `set_linewidth(width)`, `set_linestyle(style)`, `set_lighting(lighting)` | Update line width, line pattern, or lighting using the common style options. |
| `remove()` | Remove the plot and its dependent markers or annotations from the axes. |

```python
surface = ax.plot_surface(t, t, z, cmap="viridis")
surface.set_values(np.sin(x) * np.cos(y))
surface.set_clim(-1, 1)
surface.set_alpha(.8)
fig.colorbar(surface, ax=ax)
```

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
