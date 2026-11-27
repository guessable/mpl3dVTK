"""Draw plot_rc. Generated from docs/scene.md."""
from argparse import ArgumentParser
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import mpl3d_vtk


STYLE = {
    'figure.figsize': (4.25, 3.15),
    'figure.constrained_layout.use': True,
    'figure.constrained_layout.h_pad': 0.15,
    'figure.constrained_layout.w_pad': 0.18,
    'axes.titlepad': 7,
}


def draw():
    t = np.linspace(-1, 1, 41)
    x, y = np.meshgrid(t, t)
    z = .55 * np.cos(2*x) * np.sin(2*y)


    def new_scene(columns=1):
        fig, axes = plt.subplots(1, columns, figsize=(3.8*columns, 3.65), layout="constrained",
                                 subplot_kw={"projection": "vtk3d"})
        for ax in np.atleast_1d(axes):
            ax.set(xlabel="x", ylabel="y", zlabel="z")
        return fig, axes


    def sample(ax, **style):
        return ax.plot_surface(x, y, z, **style)

    from my_mpl_style import plot_rc as previous_style

    fig = plt.figure(figsize=(10.6, 10.9), layout="constrained")
    fig.get_layout_engine().set(w_pad=.14, h_pad=.12)
    time = np.linspace(0, 2*np.pi, 300)
    coordinates = np.linspace(-3, 3, 101)
    a, b = np.meshgrid(coordinates, coordinates)
    field = (3*(1-a)**2 * np.exp(-a*a-(b+1)**2)
             - 10*(a/5-a**3-b**5) * np.exp(-a*a-b*b)
             - np.exp(-(a+1)**2-b*b)/3)
    styles = ((previous_style, "my-mpl-style"), (mpl3d_vtk.plot_rc, "mpl3d-vtk"))

    for column, (style, title) in enumerate(styles, start=1):
        with plt.rc_context():
            plt.rcdefaults()
            style(grid=True)
            lines = fig.add_subplot(3, 2, column)
            for i in range(7):
                signal = i + .35*np.sin(2*time + i*.6)*np.exp(-.12*time)
                lines.plot(time, signal, label=f"Series {i + 1}")
            lines.set(title=title, xlabel="Time", ylabel="Amplitude",
                      ylim=(-.6, 9.4), yticks=[0, 2, 4, 6, 8])
            lines.legend(loc="upper right", ncols=3)

            contours = fig.add_subplot(3, 2, column + 2)
            filled = contours.contourf(a, b, field, levels=np.arange(-7, 10), cmap=plt.get_cmap())
            contours.set(title="Filled contours", xlabel="x", ylabel="y", aspect="equal")
            fig.colorbar(filled, ax=contours, shrink=.88, ticks=[-6, -2, 2, 6])

            ax = fig.add_subplot(3, 2, column + 4, projection="vtk3d")
            surface = ax.plot_surface(a, b, field, cmap=plt.get_cmap(), vmin=-7, vmax=9)
            ax.set(xlim=(-3, 3), ylim=(-3, 3), zlim=(-7, 9),
                   xticks=[-3, 0, 3], yticks=[-3, 0, 3], zticks=[-5, 0, 5],
                   title="3D surface", xlabel="x", ylabel="y", zlabel="z")
            if column == 1:
                ax.set_box_aspect((1, 1, .7))
                ax.set_proj_type("ortho")
                ax.view_init(elev=30, azim=-127.5)
            else:
                mpl3d_vtk.ax_setting(ax, box_aspect=(1, 1, .7))
            fig.colorbar(surface, ax=ax, shrink=.65, ticks=[-6, -2, 2, 6])
            fig.canvas.draw()
    return fig


def save(output):
    with plt.rc_context(STYLE):
        try:
            fig = draw()
            fig.suptitle('plot_rc', fontfamily="monospace", fontsize=12)
            fig.savefig(output, facecolor="white", dpi=140)
        finally:
            for number in plt.get_fignums():
                fig = plt.figure(number)
                for ax in fig.axes:
                    if isinstance(ax, mpl3d_vtk.VtkAxes):
                        ax.remove()
                plt.close(fig)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", type=Path, default=Path("plot_rc.png"))
    save(parser.parse_args().output)
