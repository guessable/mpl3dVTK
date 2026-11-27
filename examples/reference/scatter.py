"""Draw scatter. Generated from docs/api.md."""
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
    fig, ax = plt.subplots(subplot_kw={"projection": "vtk3d"})
    t = np.linspace(-2, 2, 61)
    x, y = np.meshgrid(t, t)
    z = np.exp(x * np.sin(y))

    theta = np.linspace(0, 4*np.pi, 56)
    heights = np.linspace(-1, 1, len(theta))
    points = ax.scatter(np.cos(theta), np.sin(theta), heights, s=24, c=heights, cmap="viridis")
    fig.colorbar(points, ax=ax)

    for panel in fig.axes:
        if isinstance(panel, mpl3d_vtk.VtkAxes):
            mpl3d_vtk.ax_setting(panel)
    return fig


def save(output):
    with plt.rc_context(STYLE):
        mpl3d_vtk.plot_rc(save_bbox="standard")
        try:
            fig = draw()
            fig.get_layout_engine().set(rect=(.06, .10, .88, .87))
            fig.suptitle('scatter', fontfamily="monospace", fontsize=12)
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
    parser.add_argument("output", nargs="?", type=Path, default=Path("scatter.png"))
    save(parser.parse_args().output)
