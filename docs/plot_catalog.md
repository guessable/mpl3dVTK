# Gallery

Click a figure to open its API reference. The link below it opens the Python code that draws it.

- **Plot data** · [Isosurfaces and triangle meshes](#isosurfaces-and-triangle-meshes) · [Surfaces](#surfaces-and-contours) · [Charts](#lines-points-and-charts) · [Scalar fields](#meshes-and-scalar-fields) · [Vector fields](#vector-fields-and-streamlines) · [Spatial geometry](#point-clouds-and-other-geometry)
- **Manage the scene** · [Axes](#axes-controls) · [Streaming lines and lights](#streaming-lines-and-lights) · [Renderer integration](#renderer-integration)
- **Work with a handle** · [Inspect geometry and data](#graphic-handles) · [Update data and colors](#update-data-and-colors) · [Style and visibility](#style-and-visibility)

## Isosurfaces and triangle meshes

These figures use the original triangle meshes and all three PFC scalar volumes.
[Get the upstream data](examples.md#upstream-data) · [Compare with mplot3d](../benchmarks/results/my_mpl_style/README.md)

<table>
  <tr>
    <td align="center" width="50%"><a href="function_reference.md#plot_isosurface"><img src="gallery/reference/plot_isosurface.png" width="420" alt="plot_isosurface. All three original PFC volumes rendered as green zero isosurfaces"></a><br><a href="../examples/reference_sources.py#L163">Source code</a></td>
    <td align="center" width="50%"><a href="function_reference.md#extract_isosurface"><img src="gallery/reference/extract_isosurface.png" width="420" alt="extract_isosurface. The first original zero isosurface extracted as triangles and colored by its Z coordinate"></a><br><a href="../examples/reference_sources.py#L148">Source code</a></td>
  </tr>
  <tr>
    <td align="center" width="50%"><a href="api.md#plot_trisurf"><img src="gallery/reference/plot_trisurf.png" width="420" alt="plot_trisurf. The original cheese mesh with per-face scalar colors and the peanut mesh with blue triangle edges"></a><br><a href="../examples/reference_sources.py#L65">Source code</a></td>
    <td align="center" width="50%"><a href="function_reference.md#plot_mesh"><img src="gallery/reference/plot_mesh.png" width="420" alt="plot_mesh. The original peanut mesh drawn from its stored XYZ vertices and triangle indices"></a><br><a href="../examples/reference_sources.py#L137">Source code</a></td>
  </tr>
</table>

## Surfaces and contours

<table>
  <tr>
    <td align="center" width="33%"><a href="api.md#plot_surface"><img src="gallery/reference/plot_surface.png" width="280" alt="plot_surface. Exponential surface colored by its height, with a scalar colorbar"></a><br><a href="../examples/reference_sources.py#L51">Source code</a></td>
    <td align="center" width="33%"><a href="api.md#plot_wireframe"><img src="gallery/reference/plot_wireframe.png" width="280" alt="plot_wireframe. A sampled line mesh over the exponential height field"></a><br><a href="../examples/reference_sources.py#L59">Source code</a></td>
    <td align="center" width="33%"><a href="api.md#contour"><img src="gallery/reference/contour.png" width="280" alt="contour. A transparent surface with three contour levels projected below it"></a><br><a href="../examples/reference_sources.py#L89">Source code</a></td>
  </tr>
</table>

## Lines, points, and charts

<table>
  <tr>
    <td align="center" width="33%"><a href="api.md#plot"><img src="gallery/reference/plot.png" width="280" alt="plot. A blue three-dimensional helix with a legend"></a><br><a href="../examples/reference_sources.py#L96">Source code</a></td>
    <td align="center" width="33%"><a href="api.md#scatter"><img src="gallery/reference/scatter.png" width="280" alt="scatter. Points on a helix colored by their individual heights"></a><br><a href="../examples/reference_sources.py#L105">Source code</a></td>
    <td align="center" width="33%"><a href="api.md#quiver"><img src="gallery/reference/quiver.png" width="280" alt="quiver. An array of arrows showing the directions of a swirling vector field"></a><br><a href="../examples/reference_sources.py#L114">Source code</a></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="api.md#bar3d"><img src="gallery/reference/bar3d.png" width="280" alt="bar3d. Three cuboid bars colored according to their heights"></a><br><a href="../examples/reference_sources.py#L123">Source code</a></td>
    <td align="center" width="33%"><a href="api.md#stem"><img src="gallery/reference/stem.png" width="280" alt="stem. Markers at the ends of vertical lines from a common baseline"></a><br><a href="../examples/reference_sources.py#L130">Source code</a></td>
  </tr>
</table>

## Meshes and scalar fields

<table>
  <tr>
    <td align="center" width="33%"><a href="function_reference.md#plot_volume_slices"><img src="gallery/reference/plot_volume_slices.png" width="280" alt="plot_volume_slices. Three perpendicular scalar slices with a shared colorbar"></a><br><a href="../examples/reference_sources.py#L183">Source code</a></td>
    <td align="center" width="33%"><a href="function_reference.md#plot_slice_contours"><img src="gallery/reference/plot_slice_contours.png" width="280" alt="plot_slice_contours. Two sets of scalar contour rings in parallel planes"></a><br><a href="../examples/reference_sources.py#L191">Source code</a></td>
    <td align="center" width="33%"><a href="function_reference.md#plot_volume"><img src="gallery/reference/plot_volume.png" width="280" alt="plot_volume. Maximum intensity projection of a Gaussian scalar volume"></a><br><a href="../examples/reference_sources.py#L198">Source code</a></td>
  </tr>
</table>

## Vector fields and streamlines

<table>
  <tr>
    <td align="center" width="33%"><a href="function_reference.md#trace_streamlines"><img src="gallery/reference/trace_streamlines.png" width="280" alt="trace_streamlines. Two seed points and the integrated paths winding upward around the Z axis"></a><br><a href="../examples/reference_sources.py#L206">Source code</a></td>
    <td align="center" width="33%"><a href="function_reference.md#plot_vector_samples"><img src="gallery/reference/plot_vector_samples.png" width="280" alt="plot_vector_samples. Arrows sampled from a continuous vector field"></a><br><a href="../examples/reference_sources.py#L215">Source code</a></td>
    <td align="center" width="33%"><a href="function_reference.md#plot_streamlines"><img src="gallery/reference/plot_streamlines.png" width="280" alt="plot_streamlines. Two curved trajectories drawn as blue lines"></a><br><a href="../examples/reference_sources.py#L224">Source code</a></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="function_reference.md#plot_streamtubes"><img src="gallery/reference/plot_streamtubes.png" width="280" alt="plot_streamtubes. Two smooth orange tubes following seeded paths"></a><br><a href="../examples/reference_sources.py#L231">Source code</a></td>
    <td align="center" width="33%"><a href="function_reference.md#plot_streamribbons"><img src="gallery/reference/plot_streamribbons.png" width="280" alt="plot_streamribbons. Purple strips twisting as they follow two streamlines"></a><br><a href="../examples/reference_sources.py#L238">Source code</a></td>
  </tr>
</table>

## Point clouds and other geometry

<table>
  <tr>
    <td align="center" width="33%"><a href="function_reference.md#plot_point_cloud"><img src="gallery/reference/plot_point_cloud.png" width="280" alt="plot_point_cloud. A cloud of sampled Gaussian points colored by height"></a><br><a href="../examples/reference_sources.py#L246">Source code</a></td>
    <td align="center" width="33%"><a href="function_reference.md#plot_alpha_shape"><img src="gallery/reference/plot_alpha_shape.png" width="280" alt="plot_alpha_shape. A partly transparent triangular boundary of a three-dimensional point cloud"></a><br><a href="../examples/reference_sources.py#L253">Source code</a></td>
    <td align="center" width="33%"><a href="function_reference.md#plot_coordinate_frames"><img src="gallery/reference/plot_coordinate_frames.png" width="280" alt="plot_coordinate_frames. Two sets of colored XYZ basis arrows"></a><br><a href="../examples/reference_sources.py#L260">Source code</a></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="function_reference.md#plot_graph"><img src="gallery/reference/plot_graph.png" width="280" alt="plot_graph. Three labeled nodes joined by directed graph edges"></a><br><a href="../examples/reference_sources.py#L267">Source code</a></td>
    <td align="center" width="33%"><a href="function_reference.md#plot_image_plane"><img src="gallery/reference/plot_image_plane.png" width="280" alt="plot_image_plane. A scalar image embedded as a textured plane in 3D"></a><br><a href="../examples/reference_sources.py#L275">Source code</a></td>
  </tr>
</table>

## Axes controls

<table>
  <tr>
    <td align="center" width="33%"><a href="scene.md#vtkaxes"><img src="gallery/reference/vtkaxes.png" width="280" alt="VtkAxes. A vtk3d subplot showing a surface with a changed camera angle"></a><br><a href="../examples/reference_sources.py#L286">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#vtkaxesset"><img src="gallery/reference/axes_set.png" width="280" alt="VtkAxes.set. A surface with axis labels, title, and limits set in one call"></a><br><a href="../examples/reference_sources.py#L294">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#get_antialiasing"><img src="gallery/reference/get_antialiasing.png" width="280" alt="get_antialiasing. A surface with its current supersampling scale in the subplot title"></a><br><a href="../examples/reference_sources.py#L303">Source code</a></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="scene.md#set_antialiasing"><img src="gallery/reference/set_antialiasing.png" width="280" alt="set_antialiasing. The same enlarged surface edges with 1× and 4× supersampling"></a><br><a href="../examples/reference_sources.py#L311">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#set_aspect"><img src="gallery/reference/set_aspect.png" width="280" alt="set_aspect. A shallow surface shown with automatic proportions and equal data units"></a><br><a href="../examples/reference_sources.py#L326">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#set_box_aspect"><img src="gallery/reference/set_box_aspect.png" width="280" alt="set_box_aspect. Two copies of a surface with the default and a taller Z box aspect"></a><br><a href="../examples/reference_sources.py#L338">Source code</a></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="scene.md#fit"><img src="gallery/reference/fit.png" width="280" alt="fit. A surface with manual limits and with limits fitted to the plotted data"></a><br><a href="../examples/reference_sources.py#L349">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#clear_scene"><img src="gallery/reference/clear_scene.png" width="280" alt="clear_scene. Removing VTK geometry leaves the Matplotlib annotation and axes in place"></a><br><a href="../examples/reference_sources.py#L362">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#clear"><img src="gallery/reference/clear.png" width="280" alt="clear. The populated subplot before clearing and the reset axes after clearing"></a><br><a href="../examples/reference_sources.py#L375">Source code</a></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="scene.md#vtkaxesremove"><img src="gallery/reference/axes_remove.png" width="280" alt="VtkAxes.remove. One of the two original subplots remains after removing the other"></a><br><a href="../examples/reference_sources.py#L386">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#get_legend_handles_labels"><img src="gallery/reference/get_legend_handles_labels.png" width="280" alt="get_legend_handles_labels. The samples legend entry placed ahead of the path entry"></a><br><a href="../examples/reference_sources.py#L396">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#legend"><img src="gallery/reference/legend.png" width="280" alt="legend. A legend identifying two curves in the same three-dimensional scene"></a><br><a href="../examples/reference_sources.py#L406">Source code</a></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="scene.md#pixels"><img src="gallery/reference/pixels.png" width="280" alt="pixels. A standalone image of the surface read back from the VTK viewport"></a><br><a href="../examples/reference_sources.py#L415">Source code</a></td>
  </tr>
</table>

## Streaming lines and lights

<table>
  <tr>
    <td align="center" width="33%"><a href="scene.md#add_streaming_line"><img src="gallery/reference/add_streaming_line.png" width="280" alt="add_streaming_line. A streaming line retaining only the most recent portion of its input"></a><br><a href="../examples/reference_sources.py#L430">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#append"><img src="gallery/reference/append.png" width="280" alt="append. Two batches forming one line, with the beginning of the second batch highlighted"></a><br><a href="../examples/reference_sources.py#L439">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#get_points"><img src="gallery/reference/get_points.png" width="280" alt="get_points. Sample points read back from a streaming line and overlaid as orange markers"></a><br><a href="../examples/reference_sources.py#L451">Source code</a></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="scene.md#clear_points"><img src="gallery/reference/clear_points.png" width="280" alt="clear_points. A streaming line before clearing and after adding a new path with the same style"></a><br><a href="../examples/reference_sources.py#L462">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#add_light"><img src="gallery/reference/add_light.png" width="280" alt="add_light. A surface with the default view light and a custom warm directional light"></a><br><a href="../examples/reference_sources.py#L476">Source code</a></td>
  </tr>
</table>

## Graphic handles

<table>
  <tr>
    <td align="center" width="33%"><a href="scene.md#graphic"><img src="gallery/reference/graphic.png" width="280" alt="Graphic. A VTK sphere displayed with a directly constructed Graphic"></a><br><a href="../examples/reference_sources.py#L488">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#vertices"><img src="gallery/reference/vertices.png" width="280" alt="vertices. The returned vertices marked with orange points on their source triangle"></a><br><a href="../examples/reference_sources.py#L501">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#faces"><img src="gallery/reference/faces.png" width="280" alt="faces. Two triangle faces labeled with their indices"></a><br><a href="../examples/reference_sources.py#L510">Source code</a></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="scene.md#get_array"><img src="gallery/reference/get_array.png" width="280" alt="get_array. The plotted surface beside a histogram of its returned scalar array"></a><br><a href="../examples/reference_sources.py#L520">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#get_cmap"><img src="gallery/reference/get_cmap.png" width="280" alt="get_cmap. A fitted surface and raised markers sharing the retrieved Magma colormap"></a><br><a href="../examples/reference_sources.py#L534">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#get_clim"><img src="gallery/reference/get_clim.png" width="280" alt="get_clim. A scalar surface with the queried lower and upper color limits"></a><br><a href="../examples/reference_sources.py#L543">Source code</a></td>
  </tr>
</table>

## Update data and colors

<table>
  <tr>
    <td align="center" width="33%"><a href="scene.md#set_heights"><img src="gallery/reference/set_heights.png" width="280" alt="set_heights. The original surface and the same grid with its heights inverted"></a><br><a href="../examples/reference_sources.py#L553">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#set_values"><img src="gallery/reference/set_values.png" width="280" alt="set_values. The same surface colored first by height and then by its Y coordinate"></a><br><a href="../examples/reference_sources.py#L565">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#set_array"><img src="gallery/reference/set_array.png" width="280" alt="set_array. A surface colored by an attached scalar array of X coordinates"></a><br><a href="../examples/reference_sources.py#L576">Source code</a></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="scene.md#set_cmap"><img src="gallery/reference/set_cmap.png" width="280" alt="set_cmap. The same surface rendered with Viridis and Plasma colormaps"></a><br><a href="../examples/reference_sources.py#L585">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#set_clim"><img src="gallery/reference/set_clim.png" width="280" alt="set_clim. The same scalar field with a wide and a narrow color range"></a><br><a href="../examples/reference_sources.py#L596">Source code</a></td>
  </tr>
</table>

## Style and visibility

<table>
  <tr>
    <td align="center" width="33%"><a href="scene.md#graphicset"><img src="gallery/reference/graphic_set.png" width="280" alt="Graphic.set. A surface with face color, edge color, line width, and opacity updated together"></a><br><a href="../examples/reference_sources.py#L607">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#set_color"><img src="gallery/reference/set_color.png" width="280" alt="set_color. Scalar-colored geometry beside the same geometry with a uniform orange color"></a><br><a href="../examples/reference_sources.py#L616">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#set_facecolor"><img src="gallery/reference/set_facecolor.png" width="280" alt="set_facecolor. A polygon grid changing face color while keeping its dark blue edges"></a><br><a href="../examples/reference_sources.py#L627">Source code</a></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="scene.md#set_edgecolor"><img src="gallery/reference/set_edgecolor.png" width="280" alt="set_edgecolor. The same coarse grid without edges and with dark polygon edges"></a><br><a href="../examples/reference_sources.py#L638">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#set_alpha"><img src="gallery/reference/set_alpha.png" width="280" alt="set_alpha. Markers behind a surface become visible when its opacity is reduced"></a><br><a href="../examples/reference_sources.py#L649">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#set_visible"><img src="gallery/reference/set_visible.png" width="280" alt="set_visible. A surface can be hidden while independently plotted points remain visible"></a><br><a href="../examples/reference_sources.py#L661">Source code</a></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="scene.md#set_linewidth"><img src="gallery/reference/set_linewidth.png" width="280" alt="set_linewidth. A thin curve and a widened version of the same curve"></a><br><a href="../examples/reference_sources.py#L673">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#set_linestyle"><img src="gallery/reference/set_linestyle.png" width="280" alt="set_linestyle. A three-dimensional curve with a legend proxy showing its requested dashed style"></a><br><a href="../examples/reference_sources.py#L684">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#set_lighting"><img src="gallery/reference/set_lighting.png" width="280" alt="set_lighting. A uniform-color surface compared with the same surface under Phong lighting"></a><br><a href="../examples/reference_sources.py#L697">Source code</a></td>
  </tr>
  <tr>
    <td align="center" width="33%"><a href="scene.md#graphicremove"><img src="gallery/reference/graphic_remove.png" width="280" alt="Graphic.remove. An independent surface remains after the orange line handle is removed"></a><br><a href="../examples/reference_sources.py#L708">Source code</a></td>
  </tr>
</table>

## Renderer integration

<table>
  <tr>
    <td align="center" width="33%"><a href="scene.md#vtkaxesdraw"><img src="gallery/reference/axes_draw.png" width="280" alt="VtkAxes.draw. A surface composited into a Matplotlib canvas by the axes draw method"></a><br><a href="../examples/reference_sources.py#L720">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#graphicdraw"><img src="gallery/reference/graphic_draw.png" width="280" alt="Graphic.draw. Two Graphic actors rendered together in one VTK viewport"></a><br><a href="../examples/reference_sources.py#L732">Source code</a></td>
    <td align="center" width="33%"><a href="scene.md#add_collection3d"><img src="gallery/reference/add_collection3d.png" width="280" alt="add_collection3d. A VTK triangle as the equivalent to adding a Matplotlib 3D polygon collection"></a><br><a href="../examples/reference_sources.py#L745">Source code</a></td>
  </tr>
</table>

## More examples

- [Three intersecting planes](examples.md#three-intersecting-planes)
- [Run the examples or regenerate these figures](examples.md#regenerate-the-reference-figures)
