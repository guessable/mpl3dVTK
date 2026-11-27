"""Draw plot_graph. Generated from docs/function_reference.md."""
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
    t = np.linspace(-1, 1, 31)
    coordinates = (t, t, t)
    x, y, z = np.meshgrid(*coordinates, indexing="xy")
    volume = x*x + y*y + z*z
    vectors = np.stack((-y, x, np.full_like(z, .2)), axis=-1)
    seeds = [[.3, 0, -.8], [.6, 0, -.8]]

    graph = ax.plot_graph([[0, 1], [1, 2], [2, 0]],
                          positions=[[0, 0, 0], [1, 0, 1], [0, 1, 0]],
                          directed=True, node_labels=["A", "B", "C"])

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
            fig.suptitle('plot_graph', fontfamily="monospace", fontsize=12)
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
    parser.add_argument("output", nargs="?", type=Path, default=Path("plot_graph.png"))
    save(parser.parse_args().output)
