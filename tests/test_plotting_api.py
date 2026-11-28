import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest
from vtk.util.numpy_support import vtk_to_numpy

import mpl_depth_style as m


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


def test_explicit_triangles_own_their_connectivity(axes):
    xyz = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, -1, 0]])
    indices = np.array([[2, 1, 0], [3, 1, 0]], dtype=np.int32)[:, ::-1]
    triangles = axes.plot_trisurf(*xyz.T, triangles=indices, values=[1, 2], association="cell")
    indices[:] = 0
    xyz[:] = 0
    np.testing.assert_array_equal(triangles.faces, [[0, 1, 2], [0, 1, 3]])
    np.testing.assert_array_equal(triangles.vertices[2], [1, 1, 0])
    with pytest.raises(ValueError, match="index"):
        axes.plot_trisurf(*xyz.T, triangles=[[0, 1, 4]])


@pytest.mark.parametrize("coordinates", ["image", "rectilinear", "curvilinear"])
def test_isosurface_interpolates_colors(axes, coordinates):
    x, y, z = (np.linspace(-1, 1, n) for n in (7, 8, 9))
    if coordinates == "rectilinear":
        x = x ** 3
    X, Y, Z = np.meshgrid(x, y, z)
    grid = (x, y, z)
    if coordinates == "curvilinear":
        X = X + Y * Z / 10
        grid = (X, Y, Z)
    h = axes.plot_isosurface(X + 2 * Y - Z, level=.2, coordinates=grid,
                             color_values=X, share_vertices=False)
    assert len(h.vertices) == 3 * len(h.faces)
    np.testing.assert_allclose(h.vertices @ [1, 2, -1], .2, atol=1e-6)
    np.testing.assert_allclose(h.get_array(), h.vertices[:, 0], atol=1e-6)


def test_lines_keep_series_and_split_at_missing_points(axes):
    t = np.arange(8.)
    lines = axes.plot(np.column_stack([t, 2 * t]), t, t)
    assert len(lines) == 2
    np.testing.assert_array_equal(lines[1].vertices[:, 0], 2 * t)
    z = np.ma.array(t, mask=[0, 0, 1, 0, 1, 0, 0, 0])
    line, = axes.plot(t, 0, z)
    assert line.data.GetNumberOfLines() == 2
    np.testing.assert_array_equal(line.vertices[:, 2], [0, 1, 5, 6, 7])


def test_scatter_masks_sizes_and_colors_with_broadcast_coordinates(axes):
    x = np.array([[0], [2]])
    y = [1, np.nan, 3]
    sizes = [1, 2, 3, 4, 5, 6]
    points = axes.scatter(x, y, 0, s=sizes, c=np.arange(6), marker="s")
    np.testing.assert_array_equal(points.vertices, [[0, 1, 0], [0, 3, 0], [2, 1, 0], [2, 3, 0]])
    np.testing.assert_array_equal(points.get_array(), [0, 2, 3, 5])
    diameter = vtk_to_numpy(points.data.GetPointData().GetArray("diameter"))
    np.testing.assert_allclose(diameter, np.sqrt([1, 3, 4, 6]))
    uniform = axes.scatter(x, y, 0, s=16)
    assert uniform.data.GetNumberOfVerts() == 4
    assert uniform.actor.GetProperty().GetPointSize() == 4


def test_transparent_vtk_render_composites_with_matplotlib(axes):
    x, y = np.meshgrid([-1.,1.], [-1.,1.])
    axes.plot_surface(x, y, np.zeros_like(x), color="red", alpha=.5, shade=False)
    axes.set_axis_off()
    axes.view_init(elev=85, azim=0)
    axes.figure.canvas.draw()
    frame = np.asarray(axes.figure.canvas.buffer_rgba())
    pixel = frame[frame.shape[0]//2, frame.shape[1]//2]
    np.testing.assert_allclose(pixel, [255,128,128,255], atol=2)


def test_plotting_api_is_focused(axes):
    for name in ("plot_mesh", "plot_volume_slices", "plot_volume", "plot_graph",
                 "plot_image_plane", "plot_streamlines", "add_streaming_line"):
        assert not hasattr(axes, name)
    for name in ("extract_isosurface", "trace_streamlines", "ax_setting"):
        assert not hasattr(m, name)
    assert m.ax3D_setting.__name__ == "ax3D_setting"


def test_legacy_entry_points_and_options_are_removed(axes):
    for name in ("surf", "patch", "quiver3", "hold", "figure", "gca", "set", "volshow", "camlight"):
        assert not hasattr(m, name)
    for name in ("surf", "quiver3", "hold", "volshow", "camlight"):
        assert not hasattr(axes, name)
    with pytest.raises(TypeError):
        axes.plot_surface([0,1], [0,1], [[0,0], [1,1]], FaceColor="red")
    with pytest.raises(TypeError):
        axes.plot_surface([0,1], [0,1], [[0,0], [1,1]], "FaceColor", "red")
