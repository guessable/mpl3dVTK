"""Draw faces. Generated from docs/scene.md."""
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

    fig, ax = new_scene()
    handle = ax.plot_mesh([[0,0,0], [1,0,0], [0,1,1], [1,1,0]], [[0,1,2], [1,3,2]],
                          color="tab:blue", alpha=.35, edgecolor="tab:blue")
    for number, face in enumerate(handle.faces):
        ax.text(*handle.vertices[face].mean(axis=0), str(number), color="black")

    for panel in fig.axes:
        if isinstance(panel, mpl3d_vtk.VtkAxes):
            mpl3d_vtk.ax_setting(panel)
    return fig


def save(output):
    with plt.rc_context(STYLE):
        try:
            fig = draw()
            fig.suptitle('faces', fontfamily="monospace", fontsize=12)
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
    parser.add_argument("output", nargs="?", type=Path, default=Path("faces.png"))
    save(parser.parse_args().output)
