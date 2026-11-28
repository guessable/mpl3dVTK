"""Draw plot_rc. Generated from docs/scene.md."""
from argparse import ArgumentParser
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import mpl_depth_style


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

    with plt.rc_context():
        mpl_depth_style.plot_rc(grid=True)
        fig = plt.figure(figsize=(10.8, 3.8), layout="constrained")
        fig.get_layout_engine().set(wspace=.16)
        curves = fig.add_subplot(131)
        for i in range(7):
            curves.plot(t, i + .35 * np.cos(4 * t + i * .6))
        curves.set(xlabel="Time", ylabel="Amplitude", title="Seven-color cycle")

        contours = fig.add_subplot(132)
        contours.contourf(x, y, z, levels=12)
        contours.set(xlabel="x", ylabel="y", aspect="equal", title="Filled contours")

        ax = fig.add_subplot(133, projection="vtk3d")
        sample(ax, cmap="viridis")
        mpl_depth_style.ax3D_setting(ax, xticks=[-1, 0, 1], yticks=[-1, 0, 1], zticks=[-.5, 0, .5])
        ax.set(xlabel="x", ylabel="y", zlabel="z", title="3D surface")
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
                    if isinstance(ax, mpl_depth_style.VtkAxes):
                        ax.remove()
                plt.close(fig)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", type=Path, default=Path("plot_rc.png"))
    save(parser.parse_args().output)
