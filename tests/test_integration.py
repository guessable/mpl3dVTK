import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton, MouseEvent
from mpl_toolkits.mplot3d import Axes3D, proj3d
import numpy as np
import pytest

import mpl3d_vtk as m
from mpl3d_vtk._projected_ticks import apply_axes_style


@pytest.fixture(autouse=True)
def close_figures():
    yield
    for number in plt.get_fignums():
        for ax in plt.figure(number).axes:
            if isinstance(ax, m.VtkAxes):
                ax.remove()
    plt.close("all")


def _figure(projection="vtk3d", **kwargs):
    return plt.subplots(figsize=(5, 4), dpi=96, subplot_kw={"projection": projection, **kwargs})


def _pixel(ax, point):
    x, y, _ = proj3d.proj_transform(*point, ax.get_proj())
    col, row = np.rint(ax.transData.transform((x, y))).astype(int)
    pixels = np.asarray(ax.figure.canvas.buffer_rgba())
    return pixels[len(pixels) - 1 - row, col, :3]


def test_identical_native_axes():
    frames = []
    for name in ("3d", "vtk3d"):
        fig, ax = _figure(name, proj_type="ortho")
        if name == "3d":
            apply_axes_style(ax)
        ax.set(xlim=(-2, 2), ylim=(1, 3), zlim=(0, 4),
               xlabel=r"$x$", ylabel=r"$y$", zlabel=r"$u$")
        ax.set_box_aspect((1, 2, 1))
        ax.view_init(elev=24, azim=46, roll=8)
        ax.tick_params(axis="z", colors="purple", labelsize=7)
        ax.zaxis.set_major_locator(matplotlib.ticker.MultipleLocator(1))
        ax.text(0, 2, 3, r"$f(x,y)$")
        fig.canvas.draw()
        frames.append(np.asarray(fig.canvas.buffer_rgba()).copy())
    np.testing.assert_array_equal(*frames)


def test_axes_defaults_and_explicit_controls():
    fig, ax = _figure()
    assert (ax.elev, ax.azim) == (30,-127.5)
    assert ax.get_aspect() == "auto"
    _, native = _figure("3d")
    assert np.isinf(ax._focal_length)
    assert all(not axis.pane.get_fill() for axis in (ax.xaxis,ax.yaxis,ax.zaxis))
    assert ax.xaxis.get_major_ticks()[0].get_pad() == -5
    assert ax.xaxis._axinfo["grid"]["linewidth"] == .2
    assert ax.xaxis.pane.get_edgecolor() == matplotlib.colors.to_rgba("gray")
    ax.plot([0,4],[0,2],[0,1])
    ax.set(xlim=(0,4), ylim=(0,2), zlim=(0,1))
    fig.canvas.draw()
    np.testing.assert_allclose(ax.get_box_aspect(), native.get_box_aspect())
    ax.set_aspect("equal")
    assert ax.get_aspect() == "equal"
    np.testing.assert_allclose(ax.get_box_aspect()/ax.get_box_aspect()[2],[4,2,1])
    ax.set_box_aspect((1,1,1))
    ax.set_zlim(0,3)
    fig.canvas.draw()
    np.testing.assert_allclose(ax.get_box_aspect()/ax.get_box_aspect()[2],[1,1,1])
    ax.clear()
    assert not ax.xaxis.pane.get_fill()
    for options in ({}, {"aspect": "auto"}):
        _, supplied = _figure(azim=105, elev=15, proj_type="persp", box_aspect=(1,1,2), **options)
        assert (supplied.elev,supplied.azim) == (15,105)
        assert np.isfinite(supplied._focal_length)
        np.testing.assert_allclose(supplied.get_box_aspect()/supplied.get_box_aspect()[0],[1,1,2])
    _, explicit_equal = _figure(aspect="equal")
    assert explicit_equal.get_aspect() == "equal"


def test_matplotlib_defaults_supply_colormap_and_color_cycle():
    style = {"image.cmap": "inferno", "axes.facecolor": "gray",
             "axes.prop_cycle": matplotlib.cycler(color=["red", "green"])}
    with matplotlib.rc_context(style):
        _, ax = _figure()
        xyz = np.array([[0., 1.], [0., 1.]])
        h = ax.plot_surface([0, 1], [0, 1], xyz, values=xyz)
        assert h.get_cmap().name == "inferno"
        assert ax.get_facecolor() == matplotlib.colors.to_rgba("gray")
        assert ax.plot_surface([0, 1], [0, 1], xyz, cmap="magma").get_cmap().name == "magma"
        surface = ax.plot_surface(xyz, xyz.T, xyz + xyz.T, cmap=None)
        assert surface.actor.GetProperty().GetColor() == (1., 0., 0.)
        lines = [ax.plot([0, 1], [0, 1], [i, i])[0] for i in (0, 1)]
        np.testing.assert_allclose([line.actor.GetProperty().GetColor() for line in lines],
                                   [matplotlib.colors.to_rgb("green"), (1., 0., 0.)])
        points = ax.scatter([0], [0], [0], color="red")
        assert points.actor.GetProperty().GetColor() == (1., 0., 0.)
        _, native = plt.subplots()
        assert native.plot([0, 1])[0].get_color() == "red"
        assert matplotlib.rcParams["image.cmap"] == "inferno"
        h.set_cmap("gray")
        ax.clear()
        assert ax.plot_surface([0, 1], [0, 1], xyz, values=xyz).get_cmap().name == "inferno"


@pytest.mark.parametrize("projection", ["persp", "ortho"])
def test_vtk_projection_and_depth(projection, monkeypatch):
    def mpl_surface(*args, **kwargs):
        pytest.fail("Matplotlib surface renderer invoked")
    monkeypatch.setattr(Axes3D, "plot_surface", mpl_surface)
    fig, ax = _figure(proj_type=projection)
    x, y = np.meshgrid([-1., 1.], [-1., 1.])
    ax.plot_surface(x, y, x, color="red", shade=False)
    ax.plot_surface(x, y, -x, color="blue", shade=False)
    ax.set(xlim=(-2, 2), ylim=(-1.5, 1.5), zlim=(-2, 2))
    ax.set_box_aspect((2, 1, 1.5))
    for elev, front in [(61, 1), (-61, -1)]:
        ax.view_init(elev=elev, azim=33, roll=12)
        fig.canvas.draw()
        np.testing.assert_array_equal(_pixel(ax, (.65, 0, .65*front)), [255,0,0] if front > 0 else [0,0,255])
        np.testing.assert_array_equal(_pixel(ax, (-.65, 0, .65*front)), [0,0,255] if front > 0 else [255,0,0])


def test_native_drag_colorbar_layout_and_export(tmp_path):
    fig = plt.figure(layout="constrained", figsize=(8, 4))
    ax = fig.add_subplot(121, projection="vtk3d")
    side = fig.add_subplot(122)
    side.plot([0,1], [0,1])
    x, y = np.meshgrid(np.linspace(-2,2,30), np.linspace(-2,2,20))
    h = ax.plot_surface(x, y, np.exp(x*np.sin(y)), cmap="viridis")
    fig.colorbar(h, ax=ax)
    h.set_clim(0,8)
    fig.canvas.draw()
    x0, y0 = ax.bbox.get_points().mean(axis=0)
    before = ax.get_proj().copy()
    for event, dx, dy in (("button_press_event",0,0), ("motion_notify_event",24,18),
                          ("button_release_event",24,18)):
        MouseEvent(event, fig.canvas, x0+dx, y0+dy, button=MouseButton.LEFT)._process()
    assert not np.allclose(before, ax.get_proj())
    assert isinstance(h, matplotlib.artist.Artist)
    assert h.get_clim() == (0,8)
    for suffix in ("png", "pdf", "svg"):
        f = tmp_path / f"surface.{suffix}"
        fig.savefig(f)
        assert f.stat().st_size > 1000
    assert "<image" in (tmp_path / "surface.svg").read_text(encoding="utf8")
    h.remove()
    assert h not in ax.artists and ax.renderer.GetActors().GetNumberOfItems() == 0
    ax.clear()
    ax.plot_surface(x, y, x+y)
    fig.canvas.draw()


def test_volume_axes_order_and_glyphs():
    _, ax = _figure()
    x, y, z = (np.linspace(a,b,n) for a,b,n in [(0,3,9),(-3,1,7),(-1,1,5)])
    X,Y,Z = np.meshgrid(x,y,z)
    v = X + 2*Y + 3*Z
    h, = ax.plot_volume_slices(v, coordinates=(x,y,z), x=1.5)
    np.testing.assert_allclose(h.vertices[:,0], 1.5)
    np.testing.assert_allclose(h.get_array(), h.vertices @ [1,2,3], atol=1e-6)
    iso = ax.plot_isosurface(v, coordinates=(x,y,z), level=1.3)
    np.testing.assert_allclose(iso.vertices @ [1,2,3], 1.3, atol=1e-6)
    g = ax.quiver([0,1],[0,0],[0,0],[1,2],[0,0],[0,0])
    assert g.mapper.IsA("vtkGlyph3DMapper")
    ax.figure.canvas.draw()


def test_supersampling_softens_edges_without_darkening_transparency():
    fig, ax = _figure()
    vertices = [[-1,-.9,0], [1,-.65,0], [-.6,1,0]]
    handle = ax.plot_mesh(vertices, [[0,1,2]], color="red")
    ax.set(xlim=(-1.5,1.5), ylim=(-1.5,1.5), zlim=(-1,1))
    ax.set_axis_off()
    ax.view_init(elev=90, azim=-90)
    assert ax.get_antialiasing() == 2
    ax.set_antialiasing(1)
    fig.canvas.draw()
    native = ax._viewport_frame
    assert set(np.unique(native[...,3])) == {0,255}

    ax.set_antialiasing(4)
    fig.canvas.draw()
    smooth = ax._viewport_frame
    height,width = smooth.shape[:2]
    assert ax.window.GetSize() == (4*width,4*height)
    assert smooth.shape == native.shape
    coverage = smooth[...,3]
    assert np.unique(coverage).size >= 8
    assert np.count_nonzero((coverage > 0) & (coverage < 255)) > 100
    assert ax.pixels(width,height) is smooth

    handle.set_alpha(.5)
    fig.canvas.draw()
    rgba = ax._viewport_frame
    covered = rgba[...,3] > 0
    assert 125 <= rgba[...,3].max() <= 129
    np.testing.assert_array_equal(rgba[covered,:3], np.tile([255,0,0],(covered.sum(),1)))


def test_supersampling_scales_screen_space_strokes_and_restores_properties():
    fig, ax = _figure(antialiasing=3)
    line, = ax.plot([0,1],[0,1],[0,1], linewidth=2.5)
    point = ax.scatter([0,1],[1,0],[0,1], s=49, c="red")
    stroke = line.actor.GetProperty()
    marker = point.actor.GetProperty()
    widths_during_render = []
    ax.window.AddObserver("StartEvent", lambda *_: widths_during_render.append(
        (stroke.GetLineWidth(), marker.GetPointSize())))
    fig.canvas.draw()
    assert (7.5,21.) in widths_during_render
    assert (stroke.GetLineWidth(), marker.GetPointSize()) == (2.5,7.)
    with pytest.raises(ValueError, match="integer from 1 to 4"):
        ax.set_antialiasing(0)


@pytest.mark.parametrize("extents", [(15.36, 18.32, 217.76, 206.72),
                                      (-8.02, 31.77, 177.01, 261.13)])
def test_viewport_rgba_compositing_matches_matplotlib_image(extents):
    from types import SimpleNamespace
    from matplotlib.backends.backend_agg import RendererAgg
    from matplotlib.image import BboxImage
    from matplotlib.transforms import Bbox
    from mpl3d_vtk._axes import _Viewport

    box = Bbox.from_extents(*extents)
    w, h = map(round, box.size)
    rgba = np.random.default_rng(7).integers(0, 256, size=(h, w, 4), dtype=np.uint8)
    bounds = (9, 7, w-14, h-11)
    left, bottom, right, top = bounds
    rgba[:bottom] = rgba[top:] = 0
    rgba[:, :left] = rgba[:, right:] = 0
    expected, actual = RendererAgg(240, 220, 100), RendererAgg(240, 220, 100)
    image = BboxImage(box, origin="lower", interpolation="nearest")
    image.set_data(rgba)
    image.draw(expected)
    viewport = _Viewport(SimpleNamespace(bbox=box, _viewport_extent=bounds,
                                         pixels=lambda width, height: rgba))
    viewport._draw_frame(actual)
    reference = np.asarray(expected.buffer_rgba())
    result = np.asarray(actual.buffer_rgba())
    np.testing.assert_array_equal(result[..., 3], reference[..., 3])
    covered = result[..., 3] > 0
    np.testing.assert_allclose(result[covered, :3], reference[covered, :3], atol=1)
