# Examples and figure export

Install the checkout so that the example scripts can import the local package.

```sh
python -m pip install -e .
```

## Three intersecting planes

Evaluate a scalar field on each plane and call [`plot_surface`](api.md#plot_surface) once per grid. Use the same color limits for all three surfaces and attach a single colorbar. The VTK depth buffer determines which parts of each plane remain visible at their intersections.

[![Three intersecting planes with a shared colorbar](gallery/intersecting_scalar_slices.png)](api.md#plot_surface)

[Documentation](api.md#plot_surface) · [Source code](../examples/intersecting_scalar_slices.py)

```sh
python examples/intersecting_scalar_slices.py intersecting_scalar_slices.png
```

## Triangle meshes and isosurfaces

The [Cheese example](api.md#plot_trisurf) colors the bundled mesh by a scalar function and adds a colorbar. For a 3D scalar array, the [random-field example](api.md#plot_isosurface) extracts the zero isosurface using seed 42.

```sh
python examples/reference/plot_trisurf.py cheese.png
python examples/random_field_isosurface.py random_field.png
```

The mesh example uses the repository's `data/cheese.npz` by default. Pass `--data-dir` to load the archives from another directory. [Example data](../data/README.md)

## Export and cleanup

Use `fig.savefig("figure.png", dpi=180)` as in a regular Matplotlib figure. SVG and PDF keep Matplotlib axes, text, and colorbars in their regular output format and embed a raster image for the VTK geometry.

The examples use the Agg Matplotlib backend for automated image generation. VTK also needs a working OpenGL context. On a headless host, use a VTK build with a supported off-screen backend such as EGL or OSMesa. Use `ax.remove()` when disposing of a VTK axes in a long-running render loop and close the figure when finished.

## Regenerate the reference figures

Run the individual scripts in [the Gallery](plot_catalog.md) or regenerate the API reference figures and their scripts in one command.

```sh
python examples/render_reference.py
python examples/random_field_isosurface.py docs/gallery/random_field_isosurface.png
python examples/intersecting_scalar_slices.py docs/gallery/intersecting_scalar_slices.png
```

Each generated reference script can also be run independently with an optional output path.

## Tests and benchmarks

```sh
python -m pip install -e ".[test]"
python -m pytest -q
python benchmarks/benchmark.py
```

The construction benchmark measures the time spent inside each plotting call. Inputs are prepared once and the benchmark reuses the axes. Setup, drawing, and file export occur outside the timing interval. The script reports runtime versions and raw samples as JSON. For rendering and rotation timings against Matplotlib's built-in projection, see the [mplot3d comparison](../benchmarks/results/my_mpl_style/README.md).

### Plot construction compared with 0.6.1

Median milliseconds over 75 measured calls per method and version, after warm-up. Both versions ran on Windows 11 with Python 3.13.5, NumPy 2.3.0, Matplotlib 3.11.0, and VTK 9.6.1.

| Method | Input | 0.6.1 (ms) | Current (ms) | Speedup |
| --- | --- | ---: | ---: | ---: |
| `plot_surface` | 600 × 600 vertices, mapped color and Gouraud lighting | 45.80 | 35.16 | 1.30× |
| `plot_trisurf` | Cheese, 307,708 triangles with explicit indices | 5.56 | 4.94 | 1.13× |
| `plot_isosurface` | 128³ scalar volume and a second field for color | 32.47 | 26.52 | 1.22× |
| `plot` | One line with 250,000 finite points | 4.79 | 2.34 | 2.04× |
| `scatter` | 250,000 finite points with uniform size and color | 8.54 | 2.28 | 3.74× |
