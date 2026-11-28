"""Draw plot_trisurf. Generated from docs/api.md."""
from argparse import ArgumentParser
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import mpl_depth_style


STYLE = {
    'figure.figsize': (4.25, 3.15),
    'figure.constrained_layout.use': True,
    'figure.constrained_layout.h_pad': 0.15,
    'figure.constrained_layout.w_pad': 0.18,
    'axes.titlepad': 7,
}


def draw(data_dir):
    fig, ax = plt.subplots(subplot_kw={"projection": "vtk3d"})
    t = np.linspace(-2, 2, 61)
    x, y = np.meshgrid(t, t)
    z = np.exp(x * np.sin(y))

    fig.set_size_inches(6.2, 5.0)
    with np.load(data_dir / "cheese.npz", allow_pickle=False) as data:
        x, y, z = data["vertices"].T
        faces = data["elements"]
    u = x * np.sin(z) + y * np.sin(x**2)
    surface = ax.plot_trisurf(x, y, z, triangles=faces, values=u[faces].mean(axis=1),
                              association="cell", cmap="viridis", vmin=u.min(), vmax=u.max(),
                              shade=False)
    ax.set_title(f"cheese · {len(faces):,} triangles")
    ax.set(xlabel="x", ylabel="y", zlabel="z")
    mpl_depth_style.ax3D_setting(ax)
    fig.colorbar(surface, ax=ax, shrink=.7, pad=.06, label=r"$u=x\sin z+y\sin(x^2)$")
    return fig


def save(output, data_dir):
    with plt.rc_context(STYLE):
        mpl_depth_style.plot_rc(save_bbox="standard")
        try:
            fig = draw(data_dir)
            fig.get_layout_engine().set(rect=(.06, .10, .88, .87))
            fig.suptitle('plot_trisurf', fontfamily="monospace", fontsize=12)
            fig.savefig(output, facecolor="white", dpi=140)
        finally:
            for number in plt.get_fignums():
                fig = plt.figure(number)
                for ax in fig.axes:
                    if isinstance(ax, mpl_depth_style.VtkAxes):
                        ax.remove()
                plt.close(fig)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", type=Path, default=Path("plot_trisurf.png"))
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parents[2] / "data")
    args = parser.parse_args()
    if not (args.data_dir / "cheese.npz").is_file():
        parser.error(f"Use --data-dir to locate cheese.npz. File not found in {args.data_dir}.")
    save(args.output, args.data_dir)
