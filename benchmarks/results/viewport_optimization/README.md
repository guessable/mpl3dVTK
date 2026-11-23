# Viewport optimization in 0.4.0

The 0.4.0 viewport passes antialiased VTK RGBA pixels directly to the Matplotlib backend. This avoids float conversion and resampling by a generic image artist. It uses direct RGBA readback when available and the VTK capture filter as a fallback.

The comparison holds the my-mpl-style axes, camera, input meshes, and 2× supersampling fixed between 0.3.1 and 0.4.0. The triangle mesh comparison had 99.9985% of pixels identical in every channel. The isosurface comparison had 99.9929%. The largest difference in the remaining channels was 1/255.

| Mesh and version | First image | Rotation median | Rotation P95 | PNG median |
| --- | ---: | ---: | ---: | ---: |
| cheese · 0.3.1 | 101.70 ms | 46.21 ms | 55.60 ms | 267.00 ms |
| cheese · 0.4.0 | 87.43 ms | 21.23 ms | 22.73 ms | 128.37 ms |
| peanut · 0.3.1 | 139.04 ms | 58.06 ms | 68.20 ms | 227.40 ms |
| peanut · 0.4.0 | 84.45 ms | 30.27 ms | 43.30 ms | 110.29 ms |

Each variant uses seven fresh figures, 30 rotations on an 800×600 Agg canvas, and seven PNG exports to memory at 1600×1200. The `cheese` mesh contains 307,708 faces and `peanut` contains 4,872. Tests ran on Windows 11 with an Intel Core i7-14650HX, NVIDIA GeForce RTX 4060 Laptop GPU, Matplotlib 3.11.0, and VTK 9.7.2. [0.3.1 samples](before/trisurf_timings.json) · [0.4.0 samples](after/trisurf_timings.json)

## Default axes

Version 0.4.0 applied my-mpl-style frames and ticks by default. With matched axis limits, its Agg axes matched the upstream `ax_setting3D` image pixel for pixel. [Reference style](https://github.com/guessable/my-mpl-style/tree/d3ab92fcaef3852701dfc2cccd22c90b5c0ecb2c)

![Cheese and peanut with the default vtk3d axes](default_axes.png)

For historical reproduction, run this command with the benchmark script and environment from each corresponding version. Use a checkout of the linked upstream revision as the first argument. For current timings, see the [triangle mesh and isosurface report](../my_mpl_style/README.md).

```sh
python benchmarks/my_mpl_style.py <checkout> <output> --mode benchmark --renderer vtk --vtk-aa 2 --source-style --rotations 30 --fresh-figures 7 --exports 7
```
