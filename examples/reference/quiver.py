"""Draw quiver. Generated from docs/api.md."""
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
    fig, ax = plt.subplots(subplot_kw={"projection": "vtk3d"})
    t = np.linspace(-2, 2, 61)
    x, y = np.meshgrid(t, t)
    z = np.exp(x * np.sin(y))

    a, b = np.meshgrid(np.linspace(-1, 1, 5), np.linspace(-1, 1, 5))
    arrows = ax.quiver(a, b, 0, -b, a, .35, length=.32, color="tab:orange")
    mpl3d_vtk.ax_setting(ax, zlim=(-.2, .65), box_aspect=(1, 1, .55))
    return fig


def save(output):
    with plt.rc_context(STYLE):
        try:
            fig = draw()
            fig.suptitle('quiver', fontfamily="monospace", fontsize=12)
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
    parser.add_argument("output", nargs="?", type=Path, default=Path("quiver.png"))
    save(parser.parse_args().output)
