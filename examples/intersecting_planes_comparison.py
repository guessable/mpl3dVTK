"""Compare split mplot3d contours, full mplot3d contours, and full vtk3d slices."""
from argparse import ArgumentParser
from pathlib import Path

from intersecting_planes import draw_planes

import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np

import mpl3d_vtk


def draw_native(ax, limits, cmap, *, split):
    t = np.linspace(*limits, 100)
    mid = sum(limits) / 2
    a, b = np.meshgrid(t, t)
    u = np.sin(10 * np.pi * (a + b + mid))
    spans = (slice(0, 50), slice(49, None)) if split else (slice(None),)
    norm = Normalize(-1, 1)
    for direction, arrays in zip("xyz", ((u, a, b), (a, u, b), (a, b, u))):
        for rows in spans:
            for columns in spans:
                ax.contourf(*(array[rows, columns] for array in arrays),
                            norm=norm, levels=100, zdir=direction, offset=mid, cmap=cmap)

    ticks = np.linspace(*limits, 3 if limits[0] == 0 else 5)
    mpl3d_vtk.ax_setting(ax, limits, limits, limits, xticks=ticks, yticks=ticks, zticks=ticks)
    ax.set(xlabel="x", ylabel="y", zlabel="z")


@plt.rc_context()
def main(output):
    mpl3d_vtk.plot_rc(save_bbox="standard")
    fig = plt.figure(figsize=(12.2, 7.7), facecolor="white")
    grid = fig.add_gridspec(2, 4, width_ratios=(1, 1, 1, .055), left=.065, right=.946,
                           bottom=.07, top=.946, wspace=.27, hspace=.16)
    titles = ("mplot3d · Original split", "mplot3d · Full planes", "vtk3d · Full planes")
    vtk_axes = []
    try:
        for row, (limits, cmap) in enumerate(zip(((0, 1), (-1, 1)), ("viridis", "plasma"))):
            axes = [fig.add_subplot(grid[row, col], projection=projection)
                    for col, projection in enumerate(("3d", "3d", "vtk3d"))]
            original, unsplit, vtk = axes
            vtk_axes.append(vtk)
            draw_native(original, limits, cmap, split=True)
            draw_native(unsplit, limits, cmap, split=False)
            surface = draw_planes(vtk, limits, cmap, "surface")
            if row == 0:
                for ax, title in zip(axes, titles):
                    ax.set_title(title, fontsize=14, pad=7)
            cax = fig.add_subplot(grid[row, 3].subgridspec(5, 1)[1:4, 0])
            fig.colorbar(surface, cax=cax, label="$u$", ticks=[-1, 0, 1])
        fig.savefig(output, dpi=150)
    finally:
        for ax in vtk_axes:
            ax.remove()
        plt.close(fig)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", type=Path, default=Path("intersecting_planes_comparison.png"))
    main(parser.parse_args().output)
