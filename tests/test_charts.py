import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.tri import Triangulation

import mpl3d_vtk


def test_matplotlib_plot_methods_draw_geometry():
    fig, ax = plt.subplots(subplot_kw={"projection": "vtk3d"})
    t = np.linspace(-2, 2, 12)
    x, y = np.meshgrid(t, t)
    z = x*x - y*y
    triangles = Triangulation([0, 1, 0, 1], [0, 0, 1, 1], [[0,1,2], [1,3,2]])
    triangles.set_mask([False, True])
    sampled = ax.plot_surface(x, y, z, rcount=3, ccount=5)
    assert len(sampled.faces) == 8
    stems = ax.stem([0, 1, 2], 0, [1, np.nan, 2], marker=None)
    assert stems.data.GetNumberOfLines() == 2
    calls = [
        lambda: ax.plot_surface(x, y, z, rstride=3, cstride=2),
        lambda: ax.plot_wireframe(x, y, z),
        lambda: ax.plot_trisurf(triangles, [0, 1, 0, 1]),
        lambda: ax.plot(t, np.sin(t), np.cos(t)),
        lambda: ax.scatter(t, np.sin(t), np.cos(t), s=np.arange(len(t)) + 1, c=t, marker="s"),
        lambda: ax.contour(t, t, z, levels=[-1, 1]),
        lambda: ax.quiver([0,1], [0,1], [0,0], [1,1], [1,1], [0,0]),
        lambda: ax.stem(t, np.sin(t), np.cos(t), bottom=-1),
        lambda: ax.bar3d([0,1], [0,0], 0, .75, .75, [1,2]),
    ]
    try:
        for draw in calls:
            ax.clear()
            draw()
            assert ax.handles
            assert any(h.data.GetNumberOfPoints() for h in ax.handles)
            fig.canvas.draw()
    finally:
        ax.remove()
        plt.close(fig)


def test_volume_contours_and_implicit_index_coordinates():
    fig, ax = plt.subplots(subplot_kw={"projection": "vtk3d"})
    try:
        x, y, z = np.meshgrid(np.arange(8), np.arange(5), np.arange(9))
        scalar = x + 2*y + z
        a, = ax.plot_slice_contours(scalar, z=2, levels=[6])
        np.testing.assert_allclose(a.vertices[:, 2], 2)
        np.testing.assert_allclose(a.vertices[:, 0] + 2*a.vertices[:, 1], 4)
        h = ax.plot_isosurface(scalar, level=8)
        assert len(h.faces) > 0
        np.testing.assert_allclose(h.vertices @ [1, 2, 1], 8, atol=1e-6)
        fig.canvas.draw()
    finally:
        ax.remove()
        plt.close(fig)
