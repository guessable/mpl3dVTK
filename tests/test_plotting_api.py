import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest
from vtk.util.numpy_support import vtk_to_numpy

import mpl3d_vtk as m


@pytest.fixture
def axes():
    fig, ax = plt.subplots(subplot_kw={"projection": "vtk3d"})
    yield ax
    ax.remove()
    plt.close(fig)


def test_surface_properties_and_native_legend(axes):
    z = np.arange(9.).reshape(3, 3)
    h = axes.plot_surface(range(3), range(3), z, cmap=np.eye(3), label="surface",
                          vertex_alpha=z / 8, lighting="gouraud", vmin=0, vmax=9)
    rgba = vtk_to_numpy(h.data.GetPointData().GetArray("display_rgba"))
    assert rgba[:, 3].min() == 0 and rgba[:, 3].max() == 255
    assert h.data.GetPointData().GetNormals().GetNumberOfTuples() == z.size
    assert axes.legend().get_texts()[0].get_text() == "surface"
    h.set(facecolor="red", linewidth=3)
    assert h.actor.GetProperty().GetLineWidth() == 3
    other = axes.plot_surface(range(3), range(3), z+1)
    assert axes.handles == [h, other]
    other.set_heights(z+2)
    np.testing.assert_allclose(other.vertices[:, 2], (z+2).ravel())
    axes.figure.canvas.draw()


def test_surface_updates_reuse_buffers_and_refresh_the_viewport(axes):
    x = y = np.arange(3)
    z = np.zeros((3, 3))
    values = np.zeros_like(z)
    h = axes.plot_surface(x, y, z, values=values, cmap="viridis", vmin=0, vmax=1)
    points = h.data.GetPoints()
    colors = h.data.GetPointData().GetArray("display_rgba")
    axes.figure.canvas.draw()
    first = axes._viewport_frame

    h.set_values(values + 1)
    axes.figure.canvas.draw()
    assert h.data.GetPointData().GetArray("display_rgba") is colors
    assert not np.array_equal(axes._viewport_frame, first)
    points_before = h.data.GetPoints()
    h.set_heights(np.where(np.eye(3, dtype=bool), np.nan, 1))
    assert len(h.faces) == 0
    masked = z.copy()
    masked[0, 0] = np.nan
    h.set_heights(masked)
    np.testing.assert_array_equal(h.faces, [[1, 2, 5, 4], [3, 4, 7, 6], [4, 5, 8, 7]])
    h.set_heights(z + 2)
    np.testing.assert_array_equal(h.faces, [[0, 1, 4, 3], [1, 2, 5, 4], [3, 4, 7, 6], [4, 5, 8, 7]])
    assert points_before is h.data.GetPoints() is points
    axes.figure.canvas.draw()


def test_contours_and_ragged_mesh(axes):
    x, y = np.meshgrid(np.linspace(-1, 1, 7), np.linspace(-1, 1, 5))
    h = axes.contour(x, y, x, levels=[-.5, .5], color="red", offset=-2)
    assert h.data.GetNumberOfLines() == 2
    np.testing.assert_allclose(np.unique(h.vertices[:, 0]), [-.5, .5])
    np.testing.assert_allclose(h.vertices[:, 2], -2)
    vertices = [[0,0,0], [1,0,0], [1,1,0], [0,1,0], [0,-1,0]]
    mesh = axes.plot_mesh(vertices, [[0,1,2,3], [0,1,4]], values=[1, 2], association="cell")
    assert [face.tolist() for face in mesh.faces] == [[0, 1, 2, 3], [0, 1, 4]]
    indices = np.array([[2, 1, 0], [4, 1, 0]], dtype=np.int32)[:, ::-1]
    triangles = axes.plot_mesh(vertices, indices)
    indices[:] = 0
    np.testing.assert_array_equal(triangles.faces, [[0, 1, 2], [0, 1, 4]])


def test_nonuniform_slice_and_flying_edges_colors(axes):
    x, y, z = [np.array(a, dtype=float) for a in ([0,1,2,4], [-1,0,1,3], [0,1,2,3,5])]
    X, Y, Z = np.meshgrid(x, y, z)
    values = X**3 + 2*Y - Z
    a, b = axes.plot_volume_slices(values, coordinates=(x,y,z), x=[1.3,1.7], interpolation="nearest")
    assert a.get_clim() == b.get_clim()
    np.testing.assert_allclose(a.vertices[:, 0], 1.3, atol=1e-6)
    np.testing.assert_allclose(b.vertices[:, 0], 1.7, atol=1e-6)
    np.testing.assert_allclose(a.get_array(), 1 + 2*a.vertices[:, 1] - a.vertices[:, 2], atol=1e-6)
    c, = axes.plot_volume_slices(values, coordinates=(x,y,z), x=1.3, interpolation="cubic")
    np.testing.assert_allclose(c.get_array(), c.vertices[:, 0]**3 + 2*c.vertices[:, 1] - c.vertices[:, 2], atol=1e-5)
    t = np.linspace(-1, 1, 7)
    X, Y, Z = np.meshgrid(t, t, t)
    g = m.extract_isosurface(X+Y+Z, level=.2, coordinates=(t,t,t), color_values=X, share_vertices=False)
    assert len(g["vertices"]) == 3*len(g["faces"])
    np.testing.assert_allclose(g["vertices"].sum(axis=1), .2, atol=1e-6)
    np.testing.assert_allclose(g["values"], g["vertices"][:, 0], atol=1e-6)


def test_lines_and_streaming_updates(axes):
    t = np.arange(5.)
    lines = axes.plot(np.column_stack([t, 2*t]), t, t)
    assert len(lines) == 2
    h = axes.add_streaming_line(max_points=3, color="red")
    h.append(t[:2], t[:2], t[:2])
    h.append(t[2:], t[2:], t[2:])
    axes.figure.canvas.draw()
    np.testing.assert_array_equal(h.get_points()[0], [2,3,4])
    h.clear_points()
    assert not len(h.get_points()[0])


def test_vector_samples_and_stream_styles(axes):
    coordinates = (np.arange(1.,6.), np.arange(1.,5.), np.arange(1.,4.))
    x, y, z = np.meshgrid(*coordinates)
    field = np.stack((np.ones_like(x), np.zeros_like(y), np.zeros_like(z)), axis=-1)
    for interpolation, expected in (("nearest", 2.), ("linear", 2.2), ("cubic", 2.2)):
        displayed = axes.plot_vector_samples(field, [[2.2,2.,2.]], coordinates=coordinates,
                                             color_values=x, interpolation=interpolation)
        np.testing.assert_allclose(displayed.get_array(), [expected], atol=1e-6)
    q = axes.quiver([0,1], [1,1], [1,1], [1,1], [0,0], [0,0], show_heads=False)
    assert q.data.GetNumberOfPoints() == 2
    path, = m.trace_streamlines(field, [2,2,2], coordinates=coordinates)
    np.testing.assert_allclose(path[:, 1:], 2)
    assert axes.plot_streamlines([path]).data.GetNumberOfLines() == 1
    h = axes.plot_streamribbons([path], twists=[np.linspace(0,1,len(path))], width=.1)
    assert h.data.GetNumberOfPolys() == len(path)-1
    assert axes.plot_streamtubes([path], radius=.2, sides=12).data.GetNumberOfCells() > 0
    axes.figure.canvas.draw()


def test_transparent_vtk_render_composites_with_matplotlib(axes):
    x, y = np.meshgrid([-1.,1.], [-1.,1.])
    axes.plot_surface(x, y, np.zeros_like(x), color="red", alpha=.5, shade=False)
    axes.set_axis_off()
    axes.view_init(elev=85, azim=0)
    axes.figure.canvas.draw()
    frame = np.asarray(axes.figure.canvas.buffer_rgba())
    pixel = frame[frame.shape[0]//2, frame.shape[1]//2]
    np.testing.assert_allclose(pixel, [255,128,128,255], atol=2)


def test_point_cloud_transforms_and_volume(axes):
    points = np.random.default_rng(18).normal(size=(320,3))
    a = axes.plot_point_cloud(points, c="#b5599b", s=9)
    b = axes.plot_point_cloud(points + [1.,0.,0.], c="#48a271", s=9)
    assert len(a.vertices) == len(b.vertices) == len(points)
    q = [np.sqrt(.5),0,0,np.sqrt(.5)]
    frames = axes.plot_coordinate_frames([[1,2,3]], rotations=q, frame_size=.5)
    vtk_vec = vtk_to_numpy(frames[0].data.GetPointData().GetVectors())
    np.testing.assert_allclose(vtk_vec, [[0,.5,0]], atol=1e-10)
    assert len(axes.plot_alpha_shape(points, radius=1.1).faces)
    axes.clear_scene()
    t = np.linspace(-1,1,29)
    x, y, z = np.meshgrid(t,t,t,sparse=True)
    volume = axes.plot_volume(np.exp(-4*(x*x+y*y+z*z)), coordinates=(t,t,t), cmap="magma",
                              opacity=[0,.02,.6], blend_mode="maximum")
    assert volume.actor.IsA("vtkVolume")
    axes.figure.colorbar(volume, ax=axes)
    axes.figure.canvas.draw()
    assert np.count_nonzero(axes._viewport_frame[..., 3]) > 100
    assert axes.handles == [volume]


def test_graph_plot_with_positions_and_force_layout(axes):
    edges = [[0,1], [1,2], [2,3], [3,0], [0,2]]
    points = np.array([[0.,0.,0.], [1.,0.,1.], [1.,1.,0.], [0.,1.,1.]])
    graph = axes.plot_graph(edges, positions=points, directed=True, node_labels=["A", "B", "C", "D"])
    np.testing.assert_allclose(graph.vertices, points)
    assert graph.data.GetNumberOfLines() == len(edges)
    assert graph.arrows.data.GetNumberOfPoints() == len(edges)
    assert len(graph.annotations) == len(points)
    laid_out = axes.plot_graph(edges)
    assert len(laid_out.vertices) == 4
    assert np.ptp(laid_out.vertices[:, 2]) > 0


def test_image_plane_with_scaled_and_indexed_color(axes):
    rgb = np.array([[[1.,0.,0.], [0.,1.,0.]], [[0.,0.,1.], [1.,1.,0.]]])
    h = axes.plot_image_plane(rgb, extent=(-.5,1.5,-.5,1.5), z=.4)
    assert h.data.GetNumberOfPolys() == 1
    np.testing.assert_allclose(h.vertices[:, 2], .4)
    assert h.texture.GetInput().GetDimensions() == (2,2,1)
    axes.set_axis_off()
    axes.view_init(elev=88, azim=-88)
    axes.figure.canvas.draw()
    pixels = axes._viewport_frame.reshape(-1, 4)
    for expected in ([255,0,0,255], [0,255,0,255], [0,0,255,255], [255,255,0,255]):
        assert np.any(np.all(pixels == expected, axis=1))
    axes.clear_scene()
    scalar = axes.plot_image_plane([[0.,1.], [2.,3.]], vmin=0., vmax=3., cmap="viridis")
    axes.figure.colorbar(scalar, ax=axes)
    scalar.set_values(np.ones((2,2)))
    np.testing.assert_allclose(scalar.get_array(), 1.)
    np.testing.assert_allclose(scalar.get_clim(), [0.,3.])
    axes.plot_image_plane([[0,1], [1,1]], z=.5, cmap=[[1,0,0], [0,1,0]],
                          norm=matplotlib.colors.NoNorm())
    axes.figure.canvas.draw()


def test_matlab_compatibility_entry_points_and_options_are_removed(axes):
    for name in ("surf", "patch", "quiver3", "hold", "figure", "gca", "set", "volshow", "camlight"):
        assert not hasattr(m, name)
    for name in ("surf", "quiver3", "hold", "volshow", "camlight"):
        assert not hasattr(axes, name)
    with pytest.raises(TypeError):
        axes.plot_surface([0,1], [0,1], [[0,0], [1,1]], FaceColor="red")
    with pytest.raises(TypeError):
        axes.plot_surface([0,1], [0,1], [[0,0], [1,1]], "FaceColor", "red")
