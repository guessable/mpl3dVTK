# mpl-depth-style

[简体中文](https://github.com/guessable/mpl-depth-style/blob/main/README.zh-CN.md)

`mpl-depth-style` adds a VTK-backed `vtk3d` projection to Matplotlib. Draw NumPy data as gridded surfaces, triangle meshes, isosurfaces, lines, and scatter plots. Use Matplotlib for axes, camera controls, colorbars, layout, and figure export.

## Installation

From the root of a source checkout, run `python -m pip install .`.

To install a published release from PyPI, run `python -m pip install mpl-depth-style`.

Requires Python 3.11+, NumPy 1.25+, Matplotlib 3.11.x, VTK 9.4–9.x, and a working OpenGL context. For headless rendering, see the [export guide](https://github.com/guessable/mpl-depth-style/blob/main/docs/examples.md#export-and-cleanup).

## Quickstart

Import `mpl_depth_style` to register the `vtk3d` projection. Call `mpl_depth_style.plot_rc()` before creating a figure to set typography, 2D styling, and a seven-color series cycle. See the [style preview](docs/scene.md#plot_rc).

```python
import matplotlib.pyplot as plt
import numpy as np
import mpl_depth_style

mpl_depth_style.plot_rc()
t = np.linspace(-2, 2, 201)
x, y = np.meshgrid(t, t)
z = np.exp(x * np.sin(y))

fig = plt.figure(figsize=(9, 4), layout="constrained")
ax = fig.add_subplot(121, projection="vtk3d")
surface = ax.plot_surface(x, y, z, cmap=plt.get_cmap())
mpl_depth_style.ax3D_setting(ax)
ax.set(xlabel="x", ylabel="y", zlabel="u")
fig.colorbar(surface, ax=ax, shrink=.7)

profile = fig.add_subplot(122)
profile.plot(t, np.exp(t))
profile.set(xlabel="x", ylabel="u", title=r"$y=\pi/2$")

fig.savefig("surface.png", dpi=180)
plt.show()
```

Use `ax.view_init()` to change the view and `surface.set_heights()` or `surface.set_values()` to update data. Multiple plots on the same axes share the VTK depth buffer.

`ax3D_setting` applies equal data scaling, an orthographic view, and projected ticks with regular-weight labels. Omitted limits and tick locations use the current axes settings. Pass `grid=False` to hide the 3D grid on that subplot.

## Examples

| Intersecting scalar slices | Random-field zero isosurface |
| --- | --- |
| ![Three intersecting scalar slices with a shared colorbar](docs/gallery/intersecting_scalar_slices.png) | ![Green zero isosurface of a seeded random field](docs/gallery/random_field_isosurface.png) |
| [Documentation](docs/api.md#plot_surface) · [Source code](examples/intersecting_scalar_slices.py) | [Documentation](docs/api.md#plot_isosurface) · [Source code](examples/random_field_isosurface.py) |

## Documentation

- [Gallery](https://github.com/guessable/mpl-depth-style/blob/main/docs/plot_catalog.md) · Browse figures with their API references and runnable Python sources.
- [Examples and export](https://github.com/guessable/mpl-depth-style/blob/main/docs/examples.md) · Run a complete script or save a figure.
- [Example datasets](https://github.com/guessable/mpl-depth-style/blob/main/data/README.md) · Load triangle meshes from NumPy archives.
- API reference · [Plotting](https://github.com/guessable/mpl-depth-style/blob/main/docs/api.md) and [Styles and plot handles](https://github.com/guessable/mpl-depth-style/blob/main/docs/scene.md).
- [Benchmarks](https://github.com/guessable/mpl-depth-style/blob/main/docs/examples.md#tests-and-benchmarks) · Measure plot construction and compare rendering with mplot3d.
