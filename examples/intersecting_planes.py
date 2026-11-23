"""Draw three perpendicular slices with VTK depth testing."""
from argparse import ArgumentParser
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import mpl3d_vtk  # Registers the vtk3d projection.


def draw_planes(ax, limits, cmap, method):
    midpoint = sum(limits) / 2
    style = {"cmap": cmap, "vmin": -1, "vmax": 1}
    if method == "surface":
        # Evaluate the analytic field at only the points that will be drawn.
        t = np.linspace(*limits, 100)
        a, b = np.meshgrid(t, t)
        c = np.full_like(a, midpoint)
        for x, y, z in ((c, a, b), (a, c, b), (a, b, c)):
            values = np.sin(10 * np.pi * (x + y + z))
            surface = ax.plot_surface(x, y, z, values=values, **style)
    else:
        # Include the midpoint in the grid so each cut lands on a sample plane.
        t = np.linspace(*limits, 101)
        x, y, z = np.meshgrid(t, t, t, sparse=True)
        volume = np.sin(10 * np.pi * (x + y + z))
        surface, *_ = ax.plot_volume_slices(volume, coordinates=(t, t, t),
                                            x=midpoint, y=midpoint, z=midpoint, **style)

    ticks = np.linspace(*limits, 3 if limits[0] == 0 else 5)
    ax.set(xticks=ticks, yticks=ticks, zticks=ticks)
    ax.set(xlim=limits, ylim=limits, zlim=limits)
    ax.set_xlabel("x", labelpad=-5)
    ax.set_ylabel("y", labelpad=-5)
    ax.set_zlabel("z", labelpad=-4)
    ax.view_init(elev=30, azim=-127.5)
    return surface


def main(output, method="surface"):
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.4), layout="constrained",
                             subplot_kw={"projection": "vtk3d"})
    try:
        for ax, limits, cmap in zip(axes, ((0, 1), (-1, 1)), ("viridis", "plasma")):
            surface = draw_planes(ax, limits, cmap, method)
            fig.colorbar(surface, ax=ax, label="$u$", shrink=.57, pad=.03, ticks=[-1, 0, 1])
        fig.savefig(output, dpi=180)
    finally:
        for ax in axes:
            ax.remove()
        plt.close(fig)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, nargs="?", default=Path("intersecting_planes.png"))
    parser.add_argument("--method", choices=("surface", "volume"), default="surface")
    args = parser.parse_args()
    main(args.output, args.method)
