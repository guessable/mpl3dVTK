"""Draw plot_vector_samples. Generated from docs/function_reference.md."""
from argparse import ArgumentParser
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoLocator, MaxNLocator
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
    t = np.linspace(-1, 1, 31)
    coordinates = (t, t, t)
    x, y, z = np.meshgrid(*coordinates, indexing="xy")
    volume = x*x + y*y + z*z
    vectors = np.stack((-y, x, np.full_like(z, .2)), axis=-1)
    seeds = [[.3, 0, -.8], [.6, 0, -.8]]

    a, b = np.meshgrid(np.linspace(-.8, .8, 6), np.linspace(-.8, .8, 6))
    sample_points = np.column_stack((a.ravel(), b.ravel(), np.zeros(a.size)))
    glyphs = ax.plot_vector_samples(vectors, sample_points, coordinates=coordinates,
                                    color_values=volume, glyph="arrow", length=.4)
    return fig


def save(output):
    with plt.rc_context(STYLE):
        try:
            fig = draw()
            for ax in fig.axes:
                if isinstance(ax, mpl3d_vtk.VtkAxes):
                    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
                        if isinstance(axis.get_major_locator(), AutoLocator):
                            axis.set_major_locator(MaxNLocator(nbins=3))
            fig.suptitle('plot_vector_samples', fontfamily="monospace", fontsize=12)
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
    parser.add_argument("output", nargs="?", type=Path, default=Path("plot_vector_samples.png"))
    save(parser.parse_args().output)
