# Plot gallery

Choose an example by input data or plot type. Each script can render a PNG from a local checkout.

![A surface beside its colorbar, a slice cutting an isosurface, 3D lines, and streamtubes](gallery/scene.png)

| Data | Plotting methods | Example |
| --- | --- | --- |
| Gridded heights | [`plot_surface`](api.md#plot_surface), [`plot_wireframe`](api.md#plot_wireframe), [`contour`](api.md#contour) | [A surface and 2D cross-sections](../examples/exp_surface.py) |
| Vertices and face indices | [`plot_mesh`](function_reference.md#plot_mesh), [`plot_trisurf`](api.md#plot_trisurf) | [A closed triangle mesh](../examples/closed_surface.py), [comparison with mplot3d](../benchmarks/results/my_mpl_style/README.md#triangle-meshes) |
| Series and observations | [`plot`](api.md#plot), [`scatter`](api.md#scatter), [`bar3d`](api.md#bar3d), [`stem`](api.md#stem) | [Matplotlib-style charts](../examples/chart_catalog.py) |
| Scalar volume | [`plot_volume`](function_reference.md#plot_volume), [`plot_isosurface`](function_reference.md#plot_isosurface), [`plot_volume_slices`](function_reference.md#plot_volume_slices), [`plot_slice_contours`](function_reference.md#plot_slice_contours) | [Intersecting planes](examples.md#three-intersecting-planes), [isosurface comparison](../benchmarks/results/my_mpl_style/README.md#zero-isosurfaces) |
| Vector field and paths | [`quiver`](api.md#quiver), [`trace_streamlines`](function_reference.md#trace_streamlines), [`plot_streamtubes`](function_reference.md#plot_streamtubes) | [Streamtubes in a swirling field](../examples/gallery.py) |
| Spatial primitives | [`plot_point_cloud`](function_reference.md#plot_point_cloud), [`plot_graph`](function_reference.md#plot_graph), [`plot_image_plane`](function_reference.md#plot_image_plane) | [VTK plot reference](../examples/function_reference.py) |

See the [examples and export guide](examples.md) for commands, file formats, and headless rendering.
