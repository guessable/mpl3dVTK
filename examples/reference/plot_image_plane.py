"""Draw plot_image_plane. Generated from docs/function_reference.md."""
from argparse import ArgumentParser
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import mpl3d_vtk

vtkplot = mpl3d_vtk


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
    t = np.linspace(-1, 1, 31)
    coordinates = (t, t, t)
    x, y, z = np.meshgrid(*coordinates, indexing="xy")
    volume = x*x + y*y + z*z
    vectors = np.stack((-y, x, np.full_like(z, .2)), axis=-1)
    seeds = [[.3, 0, -.8], [.6, 0, -.8]]

    pixels = np.sin(5*x[:, :, 0]) * np.cos(5*y[:, :, 0])
    image = ax.plot_image_plane(pixels, extent=(-1, 1, -1, 1), z=-.6,
                                cmap="coolwarm", vmin=-1, vmax=1)
    vtkplot.ax_setting(ax, (-1, 1), (-1, 1), (-.7, .5), box_aspect=(1, 1, .6))
    fig.colorbar(image, ax=ax)
    return fig


def save(output):
    with plt.rc_context(STYLE):
        try:
            fig = draw()
            fig.suptitle('plot_image_plane', fontfamily="monospace", fontsize=12)
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
    parser.add_argument("output", nargs="?", type=Path, default=Path("plot_image_plane.png"))
    save(parser.parse_args().output)
