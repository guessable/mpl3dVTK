# Gallery

Click a figure to open its API reference. The link below it opens the Python code that draws it.

- **Plot data** · [Isosurfaces and triangle meshes](#isosurfaces-and-triangle-meshes) · [Surfaces](#surfaces-and-contours) · [Charts](#lines-points-and-charts) · [Scalar fields](#meshes-and-scalar-fields) · [Vector fields](#vector-fields-and-streamlines) · [Spatial geometry](#point-clouds-and-other-geometry) · [Matplotlib aliases](#matplotlib-aliases)
- **Manage the scene** · [Axes](#axes-controls) · [Streaming lines and lights](#streaming-lines-and-lights) · [Matplotlib controls](#matplotlib-controls) · [Renderer integration](#renderer-integration)
- **Work with a handle** · [Inspect geometry and data](#graphic-handles) · [Update data and colors](#update-data-and-colors) · [Style and visibility](#style-and-visibility) · [Specialized handles](#specialized-handles)

## Isosurfaces and triangle meshes

These figures use the original triangle meshes and all three PFC scalar volumes.
[Get the upstream data](examples.md#upstream-data) · [Compare with mplot3d](../benchmarks/results/my_mpl_style/README.md)

| | |
| :---: | :---: |
| [![plot_isosurface. All three original PFC volumes rendered as green zero isosurfaces](gallery/reference/plot_isosurface.png)](function_reference.md#plot_isosurface)<br>[Source code](../examples/reference_sources.py#L185) | [![extract_isosurface. The first original zero isosurface extracted as triangles and colored by its Z coordinate](gallery/reference/extract_isosurface.png)](function_reference.md#extract_isosurface)<br>[Source code](../examples/reference_sources.py#L170) |
| [![plot_trisurf. The original cheese mesh colored by a scalar function with a colorbar](gallery/reference/plot_trisurf.png)](api.md#plot_trisurf)<br>[Source code](../examples/reference_sources.py#L65) | [![plot_mesh. The original peanut mesh drawn from its stored XYZ vertices and triangle indices](gallery/reference/plot_mesh.png)](function_reference.md#plot_mesh)<br>[Source code](../examples/reference_sources.py#L159) |

### Random isosurface

The zero level of a 19 × 19 × 19 field of uniform random samples in [−1, 1], with seed 42. Colors show vertex height.

[![plot_isosurface on a seeded random field](gallery/random_isosurface.png)](function_reference.md#plot_isosurface)

[Source code](../examples/random_isosurface.py)

## Surfaces and contours

| | | |
| :---: | :---: | :---: |
| [![plot_surface. Exponential surface colored by its height, with a scalar colorbar](gallery/reference/plot_surface.png)](api.md#plot_surface)<br>[Source code](../examples/reference_sources.py#L51) | [![plot_wireframe. A sampled line mesh over the exponential height field](gallery/reference/plot_wireframe.png)](api.md#plot_wireframe)<br>[Source code](../examples/reference_sources.py#L59) | [![contour. A transparent surface with three contour levels projected below it](gallery/reference/contour.png)](api.md#contour)<br>[Source code](../examples/reference_sources.py#L83) |

## Lines, points, and charts

| | | |
| :---: | :---: | :---: |
| [![plot. A blue three-dimensional helix with a legend](gallery/reference/plot.png)](api.md#plot)<br>[Source code](../examples/reference_sources.py#L90) | [![scatter. Points on a helix colored by their individual heights](gallery/reference/scatter.png)](api.md#scatter)<br>[Source code](../examples/reference_sources.py#L99) | [![quiver. An array of arrows showing the directions of a swirling vector field](gallery/reference/quiver.png)](api.md#quiver)<br>[Source code](../examples/reference_sources.py#L108) |
| [![bar3d. Three cuboid bars colored according to their heights](gallery/reference/bar3d.png)](api.md#bar3d)<br>[Source code](../examples/reference_sources.py#L117) | [![stem. Markers at the ends of vertical lines from a common baseline](gallery/reference/stem.png)](api.md#stem)<br>[Source code](../examples/reference_sources.py#L124) |  |

## Matplotlib aliases

| | | |
| :---: | :---: | :---: |
| [![plot3D. A helix drawn with the plot3D alias](gallery/reference/plot3d.png)](api.md#plot3d)<br>[Source code](../examples/reference_sources.py#L131) | [![scatter3D. A sampled three-dimensional point cloud drawn with scatter3D](gallery/reference/scatter3d.png)](api.md#scatter3d)<br>[Source code](../examples/reference_sources.py#L138) | [![quiver3D. Arrows on a plane drawn with quiver3D](gallery/reference/quiver3d.png)](api.md#quiver3d)<br>[Source code](../examples/reference_sources.py#L145) |
| [![contour3D. Four levels of a height field drawn with contour3D](gallery/reference/contour3d.png)](api.md#contour3d)<br>[Source code](../examples/reference_sources.py#L153) |  |  |

## Meshes and scalar fields

| | | |
| :---: | :---: | :---: |
| [![plot_volume_slices. Three perpendicular scalar slices with a shared colorbar](gallery/reference/plot_volume_slices.png)](function_reference.md#plot_volume_slices)<br>[Source code](../examples/reference_sources.py#L205) | [![plot_slice_contours. Two sets of scalar contour rings in parallel planes](gallery/reference/plot_slice_contours.png)](function_reference.md#plot_slice_contours)<br>[Source code](../examples/reference_sources.py#L213) | [![plot_volume. Maximum intensity projection of a Gaussian scalar volume](gallery/reference/plot_volume.png)](function_reference.md#plot_volume)<br>[Source code](../examples/reference_sources.py#L220) |

## Vector fields and streamlines

| | | |
| :---: | :---: | :---: |
| [![trace_streamlines. Two seed points and the integrated paths winding upward around the Z axis](gallery/reference/trace_streamlines.png)](function_reference.md#trace_streamlines)<br>[Source code](../examples/reference_sources.py#L228) | [![plot_vector_samples. Arrows sampled from a continuous vector field](gallery/reference/plot_vector_samples.png)](function_reference.md#plot_vector_samples)<br>[Source code](../examples/reference_sources.py#L237) | [![plot_streamlines. Two curved trajectories drawn as blue lines](gallery/reference/plot_streamlines.png)](function_reference.md#plot_streamlines)<br>[Source code](../examples/reference_sources.py#L246) |
| [![plot_streamtubes. Two smooth orange tubes following seeded paths](gallery/reference/plot_streamtubes.png)](function_reference.md#plot_streamtubes)<br>[Source code](../examples/reference_sources.py#L253) | [![plot_streamribbons. Purple strips twisting as they follow two streamlines](gallery/reference/plot_streamribbons.png)](function_reference.md#plot_streamribbons)<br>[Source code](../examples/reference_sources.py#L260) |  |

## Point clouds and other geometry

| | | |
| :---: | :---: | :---: |
| [![plot_point_cloud. A cloud of sampled Gaussian points colored by height](gallery/reference/plot_point_cloud.png)](function_reference.md#plot_point_cloud)<br>[Source code](../examples/reference_sources.py#L268) | [![plot_alpha_shape. A partly transparent triangular boundary of a three-dimensional point cloud](gallery/reference/plot_alpha_shape.png)](function_reference.md#plot_alpha_shape)<br>[Source code](../examples/reference_sources.py#L275) | [![plot_coordinate_frames. Two sets of colored XYZ basis arrows](gallery/reference/plot_coordinate_frames.png)](function_reference.md#plot_coordinate_frames)<br>[Source code](../examples/reference_sources.py#L282) |
| [![plot_graph. Three labeled nodes joined by directed graph edges](gallery/reference/plot_graph.png)](function_reference.md#plot_graph)<br>[Source code](../examples/reference_sources.py#L289) | [![plot_image_plane. A scalar image embedded as a textured plane in 3D](gallery/reference/plot_image_plane.png)](function_reference.md#plot_image_plane)<br>[Source code](../examples/reference_sources.py#L297) |  |

## Axes controls

| | | |
| :---: | :---: | :---: |
| [![VtkAxes. A vtk3d subplot showing a surface with a changed camera angle](gallery/reference/vtkaxes.png)](scene.md#vtkaxes)<br>[Source code](../examples/reference_sources.py#L308) | [![VtkAxes.set. A surface with axis labels, title, and limits set in one call](gallery/reference/axes_set.png)](scene.md#vtkaxesset)<br>[Source code](../examples/reference_sources.py#L316) | [![get_antialiasing. A surface with its current supersampling scale in the subplot title](gallery/reference/get_antialiasing.png)](scene.md#get_antialiasing)<br>[Source code](../examples/reference_sources.py#L325) |
| [![set_antialiasing. The same enlarged surface edges with 1× and 4× supersampling](gallery/reference/set_antialiasing.png)](scene.md#set_antialiasing)<br>[Source code](../examples/reference_sources.py#L333) | [![set_aspect. A shallow surface shown with automatic proportions and equal data units](gallery/reference/set_aspect.png)](scene.md#set_aspect)<br>[Source code](../examples/reference_sources.py#L348) | [![set_box_aspect. Two copies of a surface with the default and a taller Z box aspect](gallery/reference/set_box_aspect.png)](scene.md#set_box_aspect)<br>[Source code](../examples/reference_sources.py#L360) |
| [![fit. A surface with manual limits and with limits fitted to the plotted data](gallery/reference/fit.png)](scene.md#fit)<br>[Source code](../examples/reference_sources.py#L371) | [![clear_scene. Removing VTK geometry leaves the Matplotlib annotation and axes in place](gallery/reference/clear_scene.png)](scene.md#clear_scene)<br>[Source code](../examples/reference_sources.py#L384) | [![clear. The populated subplot before clearing and the reset axes after clearing](gallery/reference/clear.png)](scene.md#clear)<br>[Source code](../examples/reference_sources.py#L397) |
| [![VtkAxes.remove. One of the two original subplots remains after removing the other](gallery/reference/axes_remove.png)](scene.md#vtkaxesremove)<br>[Source code](../examples/reference_sources.py#L408) | [![get_legend_handles_labels. The samples legend entry placed ahead of the path entry](gallery/reference/get_legend_handles_labels.png)](scene.md#get_legend_handles_labels)<br>[Source code](../examples/reference_sources.py#L418) | [![legend. A legend identifying two curves in the same three-dimensional scene](gallery/reference/legend.png)](scene.md#legend)<br>[Source code](../examples/reference_sources.py#L428) |
| [![pixels. A standalone image of the surface read back from the VTK viewport](gallery/reference/pixels.png)](scene.md#pixels)<br>[Source code](../examples/reference_sources.py#L437) |  |  |

## Streaming lines and lights

| | | |
| :---: | :---: | :---: |
| [![add_streaming_line. A streaming line retaining only the most recent portion of its input](gallery/reference/add_streaming_line.png)](scene.md#add_streaming_line)<br>[Source code](../examples/reference_sources.py#L452) | [![append. Two batches forming one line, with the beginning of the second batch highlighted](gallery/reference/append.png)](scene.md#append)<br>[Source code](../examples/reference_sources.py#L461) | [![get_points. Sample points read back from a streaming line and overlaid as orange markers](gallery/reference/get_points.png)](scene.md#get_points)<br>[Source code](../examples/reference_sources.py#L473) |
| [![clear_points. A streaming line before clearing and after adding a new path with the same style](gallery/reference/clear_points.png)](scene.md#clear_points)<br>[Source code](../examples/reference_sources.py#L484) | [![add_light. A surface with the default view light and a custom warm directional light](gallery/reference/add_light.png)](scene.md#add_light)<br>[Source code](../examples/reference_sources.py#L498) |  |

## Graphic handles

| | | |
| :---: | :---: | :---: |
| [![Graphic. A VTK sphere displayed with a directly constructed Graphic](gallery/reference/graphic.png)](scene.md#graphic)<br>[Source code](../examples/reference_sources.py#L510) | [![vertices. The returned vertices marked with orange points on their source triangle](gallery/reference/vertices.png)](scene.md#vertices)<br>[Source code](../examples/reference_sources.py#L523) | [![faces. Two triangle faces labeled with their indices](gallery/reference/faces.png)](scene.md#faces)<br>[Source code](../examples/reference_sources.py#L532) |
| [![get_array. The plotted surface beside a histogram of its returned scalar array](gallery/reference/get_array.png)](scene.md#get_array)<br>[Source code](../examples/reference_sources.py#L542) | [![get_cmap. A fitted surface and raised markers sharing the retrieved Magma colormap](gallery/reference/get_cmap.png)](scene.md#get_cmap)<br>[Source code](../examples/reference_sources.py#L556) | [![get_clim. A scalar surface with the queried lower and upper color limits](gallery/reference/get_clim.png)](scene.md#get_clim)<br>[Source code](../examples/reference_sources.py#L565) |

## Update data and colors

| | | |
| :---: | :---: | :---: |
| [![set_heights. The original surface and the same grid with its heights inverted](gallery/reference/set_heights.png)](scene.md#set_heights)<br>[Source code](../examples/reference_sources.py#L575) | [![set_values. The same surface colored first by height and then by its Y coordinate](gallery/reference/set_values.png)](scene.md#set_values)<br>[Source code](../examples/reference_sources.py#L587) | [![set_array. A surface colored by an attached scalar array of X coordinates](gallery/reference/set_array.png)](scene.md#set_array)<br>[Source code](../examples/reference_sources.py#L598) |
| [![set_cmap. The same surface rendered with Viridis and Plasma colormaps](gallery/reference/set_cmap.png)](scene.md#set_cmap)<br>[Source code](../examples/reference_sources.py#L607) | [![set_clim. The same scalar field with a wide and a narrow color range](gallery/reference/set_clim.png)](scene.md#set_clim)<br>[Source code](../examples/reference_sources.py#L618) |  |

## Style and visibility

| | | |
| :---: | :---: | :---: |
| [![Graphic.set. A surface with face color, edge color, line width, and opacity updated together](gallery/reference/graphic_set.png)](scene.md#graphicset)<br>[Source code](../examples/reference_sources.py#L629) | [![set_color. Scalar-colored geometry beside the same geometry with a uniform orange color](gallery/reference/set_color.png)](scene.md#set_color)<br>[Source code](../examples/reference_sources.py#L638) | [![set_facecolor. A polygon grid changing face color while keeping its dark blue edges](gallery/reference/set_facecolor.png)](scene.md#set_facecolor)<br>[Source code](../examples/reference_sources.py#L649) |
| [![set_edgecolor. The same coarse grid without edges and with dark polygon edges](gallery/reference/set_edgecolor.png)](scene.md#set_edgecolor)<br>[Source code](../examples/reference_sources.py#L660) | [![set_alpha. Markers behind a surface become visible when its opacity is reduced](gallery/reference/set_alpha.png)](scene.md#set_alpha)<br>[Source code](../examples/reference_sources.py#L671) | [![set_visible. A surface can be hidden while independently plotted points remain visible](gallery/reference/set_visible.png)](scene.md#set_visible)<br>[Source code](../examples/reference_sources.py#L683) |
| [![set_linewidth. A thin curve and a widened version of the same curve](gallery/reference/set_linewidth.png)](scene.md#set_linewidth)<br>[Source code](../examples/reference_sources.py#L695) | [![set_linestyle. A three-dimensional curve with a legend proxy showing its requested dashed style](gallery/reference/set_linestyle.png)](scene.md#set_linestyle)<br>[Source code](../examples/reference_sources.py#L706) | [![set_lighting. A uniform-color surface compared with the same surface under Phong lighting](gallery/reference/set_lighting.png)](scene.md#set_lighting)<br>[Source code](../examples/reference_sources.py#L719) |
| [![Graphic.remove. An independent surface remains after the orange line handle is removed](gallery/reference/graphic_remove.png)](scene.md#graphicremove)<br>[Source code](../examples/reference_sources.py#L730) |  |  |

## Matplotlib controls

| | | |
| :---: | :---: | :---: |
| [![view_init. The same surface seen from the default and a rotated camera](gallery/reference/view_init.png)](scene.md#view_init)<br>[Source code](../examples/reference_sources.py#L742) | [![set_proj_type. One mesh seen with orthographic and perspective projection](gallery/reference/set_proj_type.png)](scene.md#set_proj_type)<br>[Source code](../examples/reference_sources.py#L754) | [![Figure.colorbar. A Plasma-colored surface with its height colorbar](gallery/reference/figure_colorbar.png)](scene.md#figurecolorbar)<br>[Source code](../examples/reference_sources.py#L766) |
| [![grid. The same surface with and without the surrounding axes grid](gallery/reference/grid.png)](scene.md#grid)<br>[Source code](../examples/reference_sources.py#L774) | [![text. A surface labeled with a text annotation at a three-dimensional position](gallery/reference/text.png)](scene.md#text)<br>[Source code](../examples/reference_sources.py#L786) | [![tick_params. A surface with enlarged red labels on the Z axis](gallery/reference/tick_params.png)](scene.md#tick_params)<br>[Source code](../examples/reference_sources.py#L794) |
| [![set_norm. The same exponential scalar field with linear and logarithmic colors](gallery/reference/set_norm.png)](scene.md#set_norm)<br>[Source code](../examples/reference_sources.py#L804) | [![set_label. A curve with its legend label set on the returned handle](gallery/reference/set_label.png)](scene.md#set_label)<br>[Source code](../examples/reference_sources.py#L818) |  |

## Specialized handles

| | | |
| :---: | :---: | :---: |
| [![VolumeGraphic.set_visible. A visible volume beside a scene where the volume is hidden and a point remains](gallery/reference/volume_set_visible.png)](scene.md#volumegraphicset_visible)<br>[Source code](../examples/reference_sources.py#L827) | [![VolumeGraphic.remove. Removing a volume leaves an independently plotted line](gallery/reference/volume_remove.png)](scene.md#volumegraphicremove)<br>[Source code](../examples/reference_sources.py#L844) | [![VolumeGraphic.draw. A VTK volume composited during a Matplotlib figure draw](gallery/reference/volume_draw.png)](scene.md#volumegraphicdraw)<br>[Source code](../examples/reference_sources.py#L861) |
| [![VolumeGraphic.set. A projected scalar volume with a label set for its legend](gallery/reference/volume_set.png)](scene.md#volumegraphicset)<br>[Source code](../examples/reference_sources.py#L874) | [![ImageGraphic.set_values. An image plane switching to new scalar pixels at the same position](gallery/reference/image_set_values.png)](scene.md#imagegraphicset_values)<br>[Source code](../examples/reference_sources.py#L887) | [![ImageGraphic.set_array. A textured plane updated with a radial scalar array and shown with its colorbar](gallery/reference/image_set_array.png)](scene.md#imagegraphicset_array)<br>[Source code](../examples/reference_sources.py#L900) |
| [![ImageGraphic.set. A translucent image plane with a legend and a line visible behind it](gallery/reference/image_set.png)](scene.md#imagegraphicset)<br>[Source code](../examples/reference_sources.py#L910) | [![StreamingLine.set. A streaming line whose color, width, and legend label were updated together](gallery/reference/streaming_line_set.png)](scene.md#streaminglineset)<br>[Source code](../examples/reference_sources.py#L921) |  |

## Renderer integration

| | | |
| :---: | :---: | :---: |
| [![VtkAxes.draw. A surface composited into a Matplotlib canvas by the axes draw method](gallery/reference/axes_draw.png)](scene.md#vtkaxesdraw)<br>[Source code](../examples/reference_sources.py#L931) | [![Graphic.draw. Two Graphic actors rendered together in one VTK viewport](gallery/reference/graphic_draw.png)](scene.md#graphicdraw)<br>[Source code](../examples/reference_sources.py#L943) | [![add_collection3d. A VTK triangle as the equivalent to adding a Matplotlib 3D polygon collection](gallery/reference/add_collection3d.png)](scene.md#add_collection3d)<br>[Source code](../examples/reference_sources.py#L956) |

## More examples

- [Three intersecting planes](examples.md#three-intersecting-planes)
- [Run the examples or regenerate these figures](examples.md#regenerate-the-reference-figures)
