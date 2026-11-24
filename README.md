# mpl3d-vtk

[简体中文](https://github.com/guessable/mpl3dVTK/blob/main/README.zh-CN.md)

`mpl3d-vtk` adds a VTK-backed `vtk3d` projection to Matplotlib. Draw NumPy data as surfaces, triangle meshes, scalar volumes, or vector fields. Use Matplotlib for axes, camera controls, colorbars, layout, and figure export.

## Installation

```sh
python -m pip install mpl3d-vtk
```

To install from a source checkout, run `python -m pip install .` from its root.

Requires Python 3.11+, NumPy 1.25+, Matplotlib 3.11.x, VTK 9.4–9.x, and a working OpenGL context. For headless rendering, see the [export guide](https://github.com/guessable/mpl3dVTK/blob/main/docs/examples.md#export-and-cleanup).

## Quickstart

Import `mpl3d_vtk` to register the projection, then create an axes with `projection="vtk3d"`.

```python
import matplotlib.pyplot as plt
import numpy as np
import mpl3d_vtk

t = np.linspace(-2, 2, 201)
x, y = np.meshgrid(t, t)
z = np.exp(x * np.sin(y))

fig = plt.figure(figsize=(9, 4), layout="constrained")
ax = fig.add_subplot(121, projection="vtk3d")
surface = ax.plot_surface(x, y, z, cmap="viridis")
ax.set(xlabel="x", ylabel="y", zlabel="u")
fig.colorbar(surface, ax=ax, shrink=.7)

profile = fig.add_subplot(122)
profile.plot(t, np.exp(t))
profile.set(xlabel="x", ylabel="u", title=r"$y=\pi/2$")

fig.savefig("surface.png", dpi=180)
plt.show()
```

Use `ax.view_init()` to change the view and `surface.set_heights()` or `surface.set_values()` to update data. Multiple plots on the same axes share the VTK depth buffer.

By default, all three axes use equal data-unit lengths and their limits span the visible plots on the axes.

## Examples

| Intersecting scalar slices | Random-field zero isosurface |
| --- | --- |
| ![Three intersecting scalar slices with a shared colorbar](docs/gallery/intersecting_scalar_slices.png) | ![Green zero isosurface of a seeded random field](docs/gallery/random_field_isosurface.png) |
| [Source code](examples/intersecting_scalar_slices.py) | [Source code](examples/random_field_isosurface.py) |

## Documentation

- [Gallery](https://github.com/guessable/mpl3dVTK/blob/main/docs/plot_catalog.md) · Browse figures with their API references and runnable Python sources.
- [Examples and export](https://github.com/guessable/mpl3dVTK/blob/main/docs/examples.md) · Run a complete script or save a figure.
- [Example datasets](https://github.com/guessable/mpl3dVTK/blob/main/data/README.md) · Load triangle meshes from NumPy archives.
- API reference · [Plotting](https://github.com/guessable/mpl3dVTK/blob/main/docs/api.md), [VTK geometry](https://github.com/guessable/mpl3dVTK/blob/main/docs/function_reference.md), and [Scene and handles](https://github.com/guessable/mpl3dVTK/blob/main/docs/scene.md).
- [Benchmarks](https://github.com/guessable/mpl3dVTK/blob/main/benchmarks/results/my_mpl_style/README.md) · Compare triangle meshes and isosurfaces with mplot3d.
