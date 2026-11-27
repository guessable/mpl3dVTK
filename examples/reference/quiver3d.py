"""Draw quiver3D. Generated from docs/api.md."""
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

    a, b = np.meshgrid(np.linspace(-1, 1, 4), np.linspace(-1, 1, 4))
    ax.quiver3D(a, b, 0, -b, a, .35, length=.42, color="tab:green")
    ax.set(zlim=(-.2, .5))

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
            fig.suptitle('quiver3D', fontfamily="monospace", fontsize=12)
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
    parser.add_argument("output", nargs="?", type=Path, default=Path("quiver3d.png"))
    save(parser.parse_args().output)
