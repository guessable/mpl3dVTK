"""Draw set_aspect. Generated from docs/scene.md."""
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
    'font.size': 9,
    'axes.titlesize': 10,
    'axes.titlepad': 7,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
}


def draw():
    t = np.linspace(-1, 1, 41)
    x, y = np.meshgrid(t, t)
    z = .55 * np.cos(2*x) * np.sin(2*y)


    def new_scene(columns=1):
        fig, axes = plt.subplots(1, columns, figsize=(3.6*columns, 3.1), layout="constrained",
                                 subplot_kw={"projection": "vtk3d"})
        for ax in np.atleast_1d(axes):
            ax.set(xlabel="x", ylabel="y", zlabel="z")
        return fig, axes


    def sample(ax, **style):
        return ax.plot_surface(x, y, z, **style)

    fig, (auto, equal) = new_scene(2)
    for ax in (auto, equal):
        ax.plot_surface(x, y, .25*z, cmap="viridis")
        mpl3d_vtk.ax_setting(ax, (-1, 1), (-1, 1), (-.2, .2), zticks=[-.2, 0, .2], aspect="auto")
    auto.set_title("Auto box proportions")
    equal.set_aspect("equal")
    equal.set_title("Equal length per data unit")
    return fig


def save(output):
    with plt.rc_context(STYLE):
        try:
            fig = draw()
            fig.suptitle('set_aspect', fontfamily="monospace", fontsize=12)
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
    parser.add_argument("output", nargs="?", type=Path, default=Path("set_aspect.png"))
    save(parser.parse_args().output)
