# ---------------------
#      "
#    '':''
#   ___:____      |\/|
# ,'        `.    \  /
# |  O        \___/  |
# ~^~^~^~^~^~^~^~^~^~^
# ---------------------
# @author: τ

"""Draw three perpendicular slices of a scalar field on a shared color scale."""

from argparse import ArgumentParser
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import mpl3d_vtk  # Registers the vtk3d projection.


def u(x, y, z):
    return np.exp(-(x**2) - y**2 - z**2) * (x + 2 * x + 3 * y)


@plt.rc_context()
def main(output=None):
    mpl3d_vtk.plot_rc(save_bbox="standard")
    coords = np.linspace(-1, 1, 100)
    a, b = np.meshgrid(coords, coords)
    zero = np.zeros_like(a)
    planes = [(a, zero, b), (zero, a, b), (a, b, zero)]
    values = [u(*plane) for plane in planes]
    vmin = min(field.min() for field in values)
    vmax = max(field.max() for field in values)
    ticks = np.linspace(-1, 1, 5)

    fig, ax = plt.subplots(figsize=(5.4, 4.35), layout="constrained",
                           subplot_kw={"projection": "vtk3d"})
    for plane, field in zip(planes, values):
        surface = ax.plot_surface(*plane, values=field, vmin=vmin, vmax=vmax)
    fig.colorbar(surface, ax=ax, label="$u$", shrink=.72, pad=.05)
    limits = (-1, 1)
    mpl3d_vtk.ax_setting(ax, limits, limits, limits, xticks=ticks, yticks=ticks, zticks=ticks)
    ax.set(xlabel="$x$", ylabel="$y$", zlabel="$z$")
    ax.set_title("plot_surface", fontfamily="monospace")

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
