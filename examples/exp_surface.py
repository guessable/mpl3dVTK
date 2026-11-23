"""Run with python examples/exp_surface.py [output.png] after installing the package."""
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator
import numpy as np
import mpl3d_vtk  # Registers the vtk3d projection.


def main(destination):
    t = np.linspace(-2, 2, 201)
    x, y = np.meshgrid(t, t)
    u = np.exp(x * np.sin(y))
    fig = plt.figure(figsize=(10.4, 5.5), dpi=160, layout="constrained")
    fig.get_layout_engine().set(h_pad=.13, w_pad=.18)
    panels = fig.add_gridspec(1, 2, width_ratios=(1.7, 1))
    ax = fig.add_subplot(panels[0], projection="vtk3d")
    profile = fig.add_subplot(panels[1])
    h = ax.plot_surface(x, y, u, vmin=np.exp(-2), vmax=np.exp(2))
    ax.set(xlabel=r"$x$", ylabel=r"$y$", zlabel=r"$u$")
    ax.set_box_aspect((1, 1, .73), zoom=.92)
    ax.xaxis.set_major_locator(FixedLocator([-2, -1, 0, 1, 2]))
    ax.yaxis.set_major_locator(FixedLocator([-1, 0, 1, 2]))
    ax.zaxis.set_major_locator(FixedLocator([0, 2, 4, 6, 8]))
    accent = "#176a75"
    ax.tick_params(axis="z", colors=accent)
    ax.zaxis.label.set_color(accent)
    ax.zaxis.pane.set_facecolor("#e7f3f4")
    ax.set(xlim=(-2, 2), ylim=(-2, 2), zlim=(0, 8))
    ax.view_init(elev=31, azim=-59)
    ax.set_title(r"$u=\exp(x\,\sin y)$", fontsize=19, pad=5)
    fig.colorbar(h, ax=ax, fraction=.043, shrink=.68, pad=.09, ticks=[1, 3, 5, 7])

    profile.plot(t, np.exp(t), color=accent, linewidth=2, label=r"$y=\pi/2$")
    profile.plot(t, np.exp(-t), color="#8558a4", linewidth=2, label=r"$y=-\pi/2$")
    profile.set(xlabel=r"$x$", ylabel=r"$u$", xlim=(-2, 2), ylim=(0, 8), title="Cross sections")
    profile.set_xticks([-2, -1, 0, 1, 2])
    profile.set_yticks([0, 2, 4, 6, 8])
    profile.tick_params(axis="y", colors=accent)
    profile.yaxis.label.set_color(accent)
    profile.spines[["top", "right"]].set_visible(False)
    profile.grid(alpha=.25)
    profile.legend(frameon=False, loc="upper center")
    fig.savefig(destination, facecolor="white")
    mpl3d_vtk.close(fig)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("exp_surface.png"))
