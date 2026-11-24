# ---------------------
#      "
#    '':''
#   ___:____      |\/|
# ,'        `.    \  /
# |  O        \___/  |
# ~^~^~^~^~^~^~^~^~^~^
# ---------------------
# @author: τ

"""Draw the zero isosurface of a seeded uniform random field."""

from argparse import ArgumentParser
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import mpl3d_vtk  # Registers the vtk3d projection.


def main(output=None):
    n = 20
    coords = np.linspace(-1, 1, n)
    values = np.random.default_rng(42).uniform(-1, 1, size=(n,) * 3)
    ticks = np.linspace(-1, 1, 5)

    fig, ax = plt.subplots(figsize=(5.4, 4.35), layout="constrained",
                           subplot_kw={"projection": "vtk3d"})
    ax.plot_isosurface(values, coordinates=(coords,) * 3, level=0, facecolor="#18b83e")
    ax.set(xticks=ticks, yticks=ticks, zticks=ticks,
           xlabel="$x$", ylabel="$y$", zlabel="$z$")
    ax.set_title("plot_isosurface", fontfamily="monospace")

    if output is None:
        plt.show()
    else:
        try:
            fig.savefig(output, dpi=160)
        finally:
            ax.remove()
            plt.close(fig)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, nargs="?", help="Image file to save")
    main(parser.parse_args().output)
