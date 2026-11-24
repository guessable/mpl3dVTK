"""Draw scatter3D. Generated from docs/api.md."""
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

    points = np.random.default_rng(6).normal(size=(90, 3))
    ax.scatter3D(*points.T, s=24, c=points[:, 2], cmap="plasma")

    for panel in fig.axes:
        if isinstance(panel, mpl3d_vtk.VtkAxes):
            mpl3d_vtk.ax_setting(panel)
    return fig


def save(output):
    with plt.rc_context(STYLE):
        try:
            fig = draw()
            fig.suptitle('scatter3D', fontfamily="monospace", fontsize=12)
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
    parser.add_argument("output", nargs="?", type=Path, default=Path("scatter3d.png"))
    save(parser.parse_args().output)
