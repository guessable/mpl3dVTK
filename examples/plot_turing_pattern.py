"""Render Turing patterns on the Armadillo and Bunny meshes."""
# Original example by τ.
from argparse import ArgumentParser
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import mpl3d_vtk  # Registers the vtk3d projection.


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATASETS = (
    ("Armadillo", "armadillo.npz", "T_end_600_spots_armadillo.npz"),
    ("Bunny", "bunny.npz", "T_end_6000_stripes_bunny.npz"),
)


def main(output=None, *, data_dir=DATA_DIR, compare=False):
    if compare:
        fig, axes = plt.subplots(2, 2, figsize=(8.4, 6.2), layout="constrained",
                                 subplot_kw={"projection": "vtk3d"})
        fig.suptitle("plot_mesh", fontfamily="monospace", fontsize=12)
    else:
        fig, axes = plt.subplots(1, 2, figsize=(11.5, 5),
                                 subplot_kw={"projection": "vtk3d"})
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0)

    for index, (name, mesh_file, field_file) in enumerate(DATASETS):
        with np.load(data_dir / mesh_file, allow_pickle=False) as mesh:
            vertices, faces = mesh["vertices"], mesh["elements"]
        with np.load(data_dir / field_file, allow_pickle=False) as field:
            u = field["u_fvm"].ravel()
        ax = axes[index, -1] if compare else axes[index]
        limits = {"vmin": u.min(), "vmax": u.max()}
        ax.plot_mesh(vertices, faces, values=u, association="point", **limits)

        if compare:
            flat_ax = axes[index, 0]
            flat_ax.plot_mesh(vertices, faces, values=u[faces].mean(axis=1),
                              association="cell", **limits)
            flat_ax.set_title(f"{name} · Face averages")
            ax.set_title(f"{name} · Interpolated vertex colors")
            for panel in (flat_ax, ax):
                panel.set_axis_off()
                panel.set_box_aspect(panel.get_box_aspect(), zoom=1.15)

    if output is None:
        plt.show()
    else:
        fig.savefig(output, dpi=160, facecolor="white")
        for ax in fig.axes:
            ax.remove()
        plt.close(fig)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", type=Path, help="Image file to save")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR, help="Directory containing the example NPZ files")
    parser.add_argument("--compare", action="store_true", help="Compare face and vertex colors")
    args = parser.parse_args()
    main(args.output, data_dir=args.data_dir, compare=args.compare)
