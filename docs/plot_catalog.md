# Gallery

Each figure links to its documentation and has a runnable Python script.

- **Plot data** · [Isosurfaces and triangle meshes](#isosurfaces-and-triangle-meshes) · [Surfaces](#surfaces-and-contours) · [Charts](#lines-points-and-charts) · [Scalar fields](#meshes-and-scalar-fields) · [Vector fields](#vector-fields-and-streamlines) · [Spatial geometry](#point-clouds-and-other-geometry) · [Matplotlib aliases](#matplotlib-aliases)
- **Manage the scene** · [Axes](#axes-controls) · [Streaming lines and lights](#streaming-lines-and-lights) · [Matplotlib controls](#matplotlib-controls) · [Renderer integration](#renderer-integration)
- **Work with a handle** · [Inspect geometry and data](#graphic-handles) · [Update data and colors](#update-data-and-colors) · [Style and visibility](#style-and-visibility) · [Specialized handles](#specialized-handles)

## Isosurfaces and triangle meshes

The triangle mesh figures use the original cheese and peanut datasets.
[Example datasets](../data/README.md) · [Compare with mplot3d](../benchmarks/results/my_mpl_style/README.md)

| | |
| :---: | :---: |
| [![plot_trisurf. The original cheese mesh colored by a scalar function with a colorbar](gallery/reference/plot_trisurf.png)](api.md#plot_trisurf)<br>[Documentation](api.md#plot_trisurf) · [Source code](../examples/reference/plot_trisurf.py) | [![plot_mesh. The original peanut mesh drawn from its stored XYZ vertices and triangle indices](gallery/reference/plot_mesh.png)](function_reference.md#plot_mesh)<br>[Documentation](function_reference.md#plot_mesh) · [Source code](../examples/reference/plot_mesh.py) |

### Random isosurface

The zero level of a 20 × 20 × 20 field of uniform random samples in [−1, 1], with seed 42.

[![plot_isosurface. Green zero isosurface of a seeded random field](gallery/random_field_isosurface.png)](function_reference.md#plot_isosurface)

[Documentation](function_reference.md#plot_isosurface) · [Source code](../examples/random_field_isosurface.py)

## Surfaces and contours

| | | |
| :---: | :---: | :---: |
| [![plot_surface. Exponential surface colored by its height, with a scalar colorbar](gallery/reference/plot_surface.png)](api.md#plot_surface)<br>[Documentation](api.md#plot_surface) · [Source code](../examples/reference/plot_surface.py) | [![plot_wireframe. A sampled line mesh over the exponential height field](gallery/reference/plot_wireframe.png)](api.md#plot_wireframe)<br>[Documentation](api.md#plot_wireframe) · [Source code](../examples/reference/plot_wireframe.py) | [![contour. A transparent surface with three contour levels projected below it](gallery/reference/contour.png)](api.md#contour)<br>[Documentation](api.md#contour) · [Source code](../examples/reference/contour.py) |

## Lines, points, and charts

| | | |
| :---: | :---: | :---: |
| [![plot. A blue three-dimensional helix with a legend](gallery/reference/plot.png)](api.md#plot)<br>[Documentation](api.md#plot) · [Source code](../examples/reference/plot.py) | [![scatter. Points on a helix colored by their individual heights](gallery/reference/scatter.png)](api.md#scatter)<br>[Documentation](api.md#scatter) · [Source code](../examples/reference/scatter.py) | [![quiver. An array of arrows showing the directions of a swirling vector field](gallery/reference/quiver.png)](api.md#quiver)<br>[Documentation](api.md#quiver) · [Source code](../examples/reference/quiver.py) |
| [![bar3d. Three cuboid bars colored according to their heights](gallery/reference/bar3d.png)](api.md#bar3d)<br>[Documentation](api.md#bar3d) · [Source code](../examples/reference/bar3d.py) | [![stem. Markers at the ends of vertical lines from a common baseline](gallery/reference/stem.png)](api.md#stem)<br>[Documentation](api.md#stem) · [Source code](../examples/reference/stem.py) |  |

## Matplotlib aliases

| | | |
| :---: | :---: | :---: |
| [![plot3D. A helix drawn with the plot3D alias](gallery/reference/plot3d.png)](api.md#plot3d)<br>[Documentation](api.md#plot3d) · [Source code](../examples/reference/plot3d.py) | [![scatter3D. A sampled three-dimensional point cloud drawn with scatter3D](gallery/reference/scatter3d.png)](api.md#scatter3d)<br>[Documentation](api.md#scatter3d) · [Source code](../examples/reference/scatter3d.py) | [![quiver3D. Arrows on a plane drawn with quiver3D](gallery/reference/quiver3d.png)](api.md#quiver3d)<br>[Documentation](api.md#quiver3d) · [Source code](../examples/reference/quiver3d.py) |
| [![contour3D. Four levels of a height field drawn with contour3D](gallery/reference/contour3d.png)](api.md#contour3d)<br>[Documentation](api.md#contour3d) · [Source code](../examples/reference/contour3d.py) |  |  |

## Meshes and scalar fields

| | | |
| :---: | :---: | :---: |
| [![plot_volume_slices. Three perpendicular scalar slices with a shared colorbar](gallery/reference/plot_volume_slices.png)](function_reference.md#plot_volume_slices)<br>[Documentation](function_reference.md#plot_volume_slices) · [Source code](../examples/reference/plot_volume_slices.py) | [![plot_slice_contours. Two sets of scalar contour rings in parallel planes](gallery/reference/plot_slice_contours.png)](function_reference.md#plot_slice_contours)<br>[Documentation](function_reference.md#plot_slice_contours) · [Source code](../examples/reference/plot_slice_contours.py) | [![plot_volume. Maximum intensity projection of a Gaussian scalar volume](gallery/reference/plot_volume.png)](function_reference.md#plot_volume)<br>[Documentation](function_reference.md#plot_volume) · [Source code](../examples/reference/plot_volume.py) |

## Vector fields and streamlines

| | | |
| :---: | :---: | :---: |
| [![trace_streamlines. Two seed points and the integrated paths winding upward around the Z axis](gallery/reference/trace_streamlines.png)](function_reference.md#trace_streamlines)<br>[Documentation](function_reference.md#trace_streamlines) · [Source code](../examples/reference/trace_streamlines.py) | [![plot_vector_samples. Arrows sampled from a continuous vector field](gallery/reference/plot_vector_samples.png)](function_reference.md#plot_vector_samples)<br>[Documentation](function_reference.md#plot_vector_samples) · [Source code](../examples/reference/plot_vector_samples.py) | [![plot_streamlines. Two curved trajectories drawn as blue lines](gallery/reference/plot_streamlines.png)](function_reference.md#plot_streamlines)<br>[Documentation](function_reference.md#plot_streamlines) · [Source code](../examples/reference/plot_streamlines.py) |
| [![plot_streamtubes. Two smooth orange tubes following seeded paths](gallery/reference/plot_streamtubes.png)](function_reference.md#plot_streamtubes)<br>[Documentation](function_reference.md#plot_streamtubes) · [Source code](../examples/reference/plot_streamtubes.py) | [![plot_streamribbons. Purple strips twisting as they follow two streamlines](gallery/reference/plot_streamribbons.png)](function_reference.md#plot_streamribbons)<br>[Documentation](function_reference.md#plot_streamribbons) · [Source code](../examples/reference/plot_streamribbons.py) |  |

## Point clouds and other geometry

| | | |
| :---: | :---: | :---: |
| [![plot_point_cloud. A cloud of sampled Gaussian points colored by height](gallery/reference/plot_point_cloud.png)](function_reference.md#plot_point_cloud)<br>[Documentation](function_reference.md#plot_point_cloud) · [Source code](../examples/reference/plot_point_cloud.py) | [![plot_alpha_shape. A partly transparent triangular boundary of a three-dimensional point cloud](gallery/reference/plot_alpha_shape.png)](function_reference.md#plot_alpha_shape)<br>[Documentation](function_reference.md#plot_alpha_shape) · [Source code](../examples/reference/plot_alpha_shape.py) | [![plot_coordinate_frames. Two sets of colored XYZ basis arrows](gallery/reference/plot_coordinate_frames.png)](function_reference.md#plot_coordinate_frames)<br>[Documentation](function_reference.md#plot_coordinate_frames) · [Source code](../examples/reference/plot_coordinate_frames.py) |
| [![plot_graph. Three labeled nodes joined by directed graph edges](gallery/reference/plot_graph.png)](function_reference.md#plot_graph)<br>[Documentation](function_reference.md#plot_graph) · [Source code](../examples/reference/plot_graph.py) | [![plot_image_plane. A scalar image embedded as a textured plane in 3D](gallery/reference/plot_image_plane.png)](function_reference.md#plot_image_plane)<br>[Documentation](function_reference.md#plot_image_plane) · [Source code](../examples/reference/plot_image_plane.py) |  |

## Axes controls

| | | |
| :---: | :---: | :---: |
| [![VtkAxes. A vtk3d subplot showing a surface with a changed camera angle](gallery/reference/vtkaxes.png)](scene.md#vtkaxes)<br>[Documentation](scene.md#vtkaxes) · [Source code](../examples/reference/vtkaxes.py) | [![VtkAxes.set. A surface with axis labels, title, and limits set in one call](gallery/reference/axes_set.png)](scene.md#vtkaxesset)<br>[Documentation](scene.md#vtkaxesset) · [Source code](../examples/reference/axes_set.py) | [![get_antialiasing. A surface with its current supersampling scale in the subplot title](gallery/reference/get_antialiasing.png)](scene.md#get_antialiasing)<br>[Documentation](scene.md#get_antialiasing) · [Source code](../examples/reference/get_antialiasing.py) |
| [![set_antialiasing. The same enlarged surface edges with 1× and 4× supersampling](gallery/reference/set_antialiasing.png)](scene.md#set_antialiasing)<br>[Documentation](scene.md#set_antialiasing) · [Source code](../examples/reference/set_antialiasing.py) | [![set_aspect. A shallow surface shown with automatic proportions and equal data units](gallery/reference/set_aspect.png)](scene.md#set_aspect)<br>[Documentation](scene.md#set_aspect) · [Source code](../examples/reference/set_aspect.py) | [![set_box_aspect. Two copies of a surface with the default and a taller Z box aspect](gallery/reference/set_box_aspect.png)](scene.md#set_box_aspect)<br>[Documentation](scene.md#set_box_aspect) · [Source code](../examples/reference/set_box_aspect.py) |
| [![fit. A surface with manual limits and with limits fitted to the plotted data](gallery/reference/fit.png)](scene.md#fit)<br>[Documentation](scene.md#fit) · [Source code](../examples/reference/fit.py) | [![clear_scene. Removing VTK geometry leaves the Matplotlib annotation and axes in place](gallery/reference/clear_scene.png)](scene.md#clear_scene)<br>[Documentation](scene.md#clear_scene) · [Source code](../examples/reference/clear_scene.py) | [![clear. The populated subplot before clearing and the reset axes after clearing](gallery/reference/clear.png)](scene.md#clear)<br>[Documentation](scene.md#clear) · [Source code](../examples/reference/clear.py) |
| [![VtkAxes.remove. One of the two original subplots remains after removing the other](gallery/reference/axes_remove.png)](scene.md#vtkaxesremove)<br>[Documentation](scene.md#vtkaxesremove) · [Source code](../examples/reference/axes_remove.py) | [![get_legend_handles_labels. The samples legend entry placed ahead of the path entry](gallery/reference/get_legend_handles_labels.png)](scene.md#get_legend_handles_labels)<br>[Documentation](scene.md#get_legend_handles_labels) · [Source code](../examples/reference/get_legend_handles_labels.py) | [![legend. A legend identifying two curves in the same three-dimensional scene](gallery/reference/legend.png)](scene.md#legend)<br>[Documentation](scene.md#legend) · [Source code](../examples/reference/legend.py) |
| [![pixels. A standalone image of the surface read back from the VTK viewport](gallery/reference/pixels.png)](scene.md#pixels)<br>[Documentation](scene.md#pixels) · [Source code](../examples/reference/pixels.py) |  |  |

## Streaming lines and lights

| | | |
| :---: | :---: | :---: |
| [![add_streaming_line. A streaming line retaining only the most recent portion of its input](gallery/reference/add_streaming_line.png)](scene.md#add_streaming_line)<br>[Documentation](scene.md#add_streaming_line) · [Source code](../examples/reference/add_streaming_line.py) | [![append. Two batches forming one line, with the beginning of the second batch highlighted](gallery/reference/append.png)](scene.md#append)<br>[Documentation](scene.md#append) · [Source code](../examples/reference/append.py) | [![get_points. Sample points read back from a streaming line and overlaid as orange markers](gallery/reference/get_points.png)](scene.md#get_points)<br>[Documentation](scene.md#get_points) · [Source code](../examples/reference/get_points.py) |
| [![clear_points. A streaming line before clearing and after adding a new path with the same style](gallery/reference/clear_points.png)](scene.md#clear_points)<br>[Documentation](scene.md#clear_points) · [Source code](../examples/reference/clear_points.py) | [![add_light. A surface with the default view light and a custom warm directional light](gallery/reference/add_light.png)](scene.md#add_light)<br>[Documentation](scene.md#add_light) · [Source code](../examples/reference/add_light.py) |  |

## Graphic handles

| | | |
| :---: | :---: | :---: |
| [![Graphic. A VTK sphere displayed with a directly constructed Graphic](gallery/reference/graphic.png)](scene.md#graphic)<br>[Documentation](scene.md#graphic) · [Source code](../examples/reference/graphic.py) | [![vertices. The returned vertices marked with orange points on their source triangle](gallery/reference/vertices.png)](scene.md#vertices)<br>[Documentation](scene.md#vertices) · [Source code](../examples/reference/vertices.py) | [![faces. Two triangle faces labeled with their indices](gallery/reference/faces.png)](scene.md#faces)<br>[Documentation](scene.md#faces) · [Source code](../examples/reference/faces.py) |
| [![get_array. The plotted surface beside a histogram of its returned scalar array](gallery/reference/get_array.png)](scene.md#get_array)<br>[Documentation](scene.md#get_array) · [Source code](../examples/reference/get_array.py) | [![get_cmap. A fitted surface and raised markers sharing the retrieved Magma colormap](gallery/reference/get_cmap.png)](scene.md#get_cmap)<br>[Documentation](scene.md#get_cmap) · [Source code](../examples/reference/get_cmap.py) | [![get_clim. A scalar surface with the queried lower and upper color limits](gallery/reference/get_clim.png)](scene.md#get_clim)<br>[Documentation](scene.md#get_clim) · [Source code](../examples/reference/get_clim.py) |

## Update data and colors

| | | |
| :---: | :---: | :---: |
| [![set_heights. The original surface and the same grid with its heights inverted](gallery/reference/set_heights.png)](scene.md#set_heights)<br>[Documentation](scene.md#set_heights) · [Source code](../examples/reference/set_heights.py) | [![set_values. The same surface colored first by height and then by its Y coordinate](gallery/reference/set_values.png)](scene.md#set_values)<br>[Documentation](scene.md#set_values) · [Source code](../examples/reference/set_values.py) | [![set_array. A surface colored by an attached scalar array of X coordinates](gallery/reference/set_array.png)](scene.md#set_array)<br>[Documentation](scene.md#set_array) · [Source code](../examples/reference/set_array.py) |
| [![set_cmap. The same surface rendered with Viridis and Plasma colormaps](gallery/reference/set_cmap.png)](scene.md#set_cmap)<br>[Documentation](scene.md#set_cmap) · [Source code](../examples/reference/set_cmap.py) | [![set_clim. The same scalar field with a wide and a narrow color range](gallery/reference/set_clim.png)](scene.md#set_clim)<br>[Documentation](scene.md#set_clim) · [Source code](../examples/reference/set_clim.py) |  |

## Style and visibility

| | | |
| :---: | :---: | :---: |
| [![Graphic.set. A surface with face color, edge color, line width, and opacity updated together](gallery/reference/graphic_set.png)](scene.md#graphicset)<br>[Documentation](scene.md#graphicset) · [Source code](../examples/reference/graphic_set.py) | [![set_color. Scalar-colored geometry beside the same geometry with a uniform orange color](gallery/reference/set_color.png)](scene.md#set_color)<br>[Documentation](scene.md#set_color) · [Source code](../examples/reference/set_color.py) | [![set_facecolor. A polygon grid changing face color while keeping its dark blue edges](gallery/reference/set_facecolor.png)](scene.md#set_facecolor)<br>[Documentation](scene.md#set_facecolor) · [Source code](../examples/reference/set_facecolor.py) |
| [![set_edgecolor. The same coarse grid without edges and with dark polygon edges](gallery/reference/set_edgecolor.png)](scene.md#set_edgecolor)<br>[Documentation](scene.md#set_edgecolor) · [Source code](../examples/reference/set_edgecolor.py) | [![set_alpha. Markers behind a surface become visible when its opacity is reduced](gallery/reference/set_alpha.png)](scene.md#set_alpha)<br>[Documentation](scene.md#set_alpha) · [Source code](../examples/reference/set_alpha.py) | [![set_visible. A surface can be hidden while independently plotted points remain visible](gallery/reference/set_visible.png)](scene.md#set_visible)<br>[Documentation](scene.md#set_visible) · [Source code](../examples/reference/set_visible.py) |
| [![set_linewidth. A thin curve and a widened version of the same curve](gallery/reference/set_linewidth.png)](scene.md#set_linewidth)<br>[Documentation](scene.md#set_linewidth) · [Source code](../examples/reference/set_linewidth.py) | [![set_linestyle. A three-dimensional curve with a legend proxy showing its requested dashed style](gallery/reference/set_linestyle.png)](scene.md#set_linestyle)<br>[Documentation](scene.md#set_linestyle) · [Source code](../examples/reference/set_linestyle.py) | [![set_lighting. A uniform-color surface compared with the same surface under Phong lighting](gallery/reference/set_lighting.png)](scene.md#set_lighting)<br>[Documentation](scene.md#set_lighting) · [Source code](../examples/reference/set_lighting.py) |
| [![Graphic.remove. An independent surface remains after the orange line handle is removed](gallery/reference/graphic_remove.png)](scene.md#graphicremove)<br>[Documentation](scene.md#graphicremove) · [Source code](../examples/reference/graphic_remove.py) |  |  |

## Matplotlib controls

| | | |
| :---: | :---: | :---: |
| [![view_init. The same surface seen from the default and a rotated camera](gallery/reference/view_init.png)](scene.md#view_init)<br>[Documentation](scene.md#view_init) · [Source code](../examples/reference/view_init.py) | [![set_proj_type. One mesh seen with orthographic and perspective projection](gallery/reference/set_proj_type.png)](scene.md#set_proj_type)<br>[Documentation](scene.md#set_proj_type) · [Source code](../examples/reference/set_proj_type.py) | [![Figure.colorbar. A Plasma-colored surface with its height colorbar](gallery/reference/figure_colorbar.png)](scene.md#figurecolorbar)<br>[Documentation](scene.md#figurecolorbar) · [Source code](../examples/reference/figure_colorbar.py) |
| [![grid. The same surface with and without the surrounding axes grid](gallery/reference/grid.png)](scene.md#grid)<br>[Documentation](scene.md#grid) · [Source code](../examples/reference/grid.py) | [![text. A surface labeled with a text annotation at a three-dimensional position](gallery/reference/text.png)](scene.md#text)<br>[Documentation](scene.md#text) · [Source code](../examples/reference/text.py) | [![tick_params. A surface with enlarged red labels on the Z axis](gallery/reference/tick_params.png)](scene.md#tick_params)<br>[Documentation](scene.md#tick_params) · [Source code](../examples/reference/tick_params.py) |
| [![set_norm. The same exponential scalar field with linear and logarithmic colors](gallery/reference/set_norm.png)](scene.md#set_norm)<br>[Documentation](scene.md#set_norm) · [Source code](../examples/reference/set_norm.py) | [![set_label. A curve with its legend label set on the returned handle](gallery/reference/set_label.png)](scene.md#set_label)<br>[Documentation](scene.md#set_label) · [Source code](../examples/reference/set_label.py) |  |

## Specialized handles

| | | |
| :---: | :---: | :---: |
| [![VolumeGraphic.set_visible. A visible volume beside a scene where the volume is hidden and a point remains](gallery/reference/volume_set_visible.png)](scene.md#volumegraphicset_visible)<br>[Documentation](scene.md#volumegraphicset_visible) · [Source code](../examples/reference/volume_set_visible.py) | [![VolumeGraphic.remove. Removing a volume leaves an independently plotted line](gallery/reference/volume_remove.png)](scene.md#volumegraphicremove)<br>[Documentation](scene.md#volumegraphicremove) · [Source code](../examples/reference/volume_remove.py) | [![VolumeGraphic.draw. A VTK volume composited during a Matplotlib figure draw](gallery/reference/volume_draw.png)](scene.md#volumegraphicdraw)<br>[Documentation](scene.md#volumegraphicdraw) · [Source code](../examples/reference/volume_draw.py) |
| [![VolumeGraphic.set. A projected scalar volume with a label set for its legend](gallery/reference/volume_set.png)](scene.md#volumegraphicset)<br>[Documentation](scene.md#volumegraphicset) · [Source code](../examples/reference/volume_set.py) | [![ImageGraphic.set_values. An image plane switching to new scalar pixels at the same position](gallery/reference/image_set_values.png)](scene.md#imagegraphicset_values)<br>[Documentation](scene.md#imagegraphicset_values) · [Source code](../examples/reference/image_set_values.py) | [![ImageGraphic.set_array. A textured plane updated with a radial scalar array and shown with its colorbar](gallery/reference/image_set_array.png)](scene.md#imagegraphicset_array)<br>[Documentation](scene.md#imagegraphicset_array) · [Source code](../examples/reference/image_set_array.py) |
| [![ImageGraphic.set. A translucent image plane with a legend and a line visible behind it](gallery/reference/image_set.png)](scene.md#imagegraphicset)<br>[Documentation](scene.md#imagegraphicset) · [Source code](../examples/reference/image_set.py) | [![StreamingLine.set. A streaming line whose color, width, and legend label were updated together](gallery/reference/streaming_line_set.png)](scene.md#streaminglineset)<br>[Documentation](scene.md#streaminglineset) · [Source code](../examples/reference/streaming_line_set.py) |  |

## Renderer integration

| | | |
| :---: | :---: | :---: |
| [![VtkAxes.draw. A surface composited into a Matplotlib canvas by the axes draw method](gallery/reference/axes_draw.png)](scene.md#vtkaxesdraw)<br>[Documentation](scene.md#vtkaxesdraw) · [Source code](../examples/reference/axes_draw.py) | [![Graphic.draw. Two Graphic actors rendered together in one VTK viewport](gallery/reference/graphic_draw.png)](scene.md#graphicdraw)<br>[Documentation](scene.md#graphicdraw) · [Source code](../examples/reference/graphic_draw.py) | [![add_collection3d. A VTK triangle as the equivalent to adding a Matplotlib 3D polygon collection](gallery/reference/add_collection3d.png)](scene.md#add_collection3d)<br>[Documentation](scene.md#add_collection3d) · [Source code](../examples/reference/add_collection3d.py) |

## More examples

- [Three intersecting planes](examples.md#three-intersecting-planes)
- [Run the examples or regenerate these figures](examples.md#regenerate-the-reference-figures)
