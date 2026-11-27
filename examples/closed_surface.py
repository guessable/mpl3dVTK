"""Plot a scalar field on a watertight torus as a triangle mesh."""
from argparse import ArgumentParser
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from vtk.util.numpy_support import numpy_to_vtk

import mpl3d_vtk  # Registers the vtk3d projection.


@plt.rc_context()
def main(destination, antialiasing=2):
    mpl3d_vtk.plot_rc(save_bbox="standard")
    theta, phi = np.meshgrid(
        np.linspace(0, 2*np.pi, 240, endpoint=False),
        np.linspace(0, 2*np.pi, 96, endpoint=False),
        indexing="ij",
    )
    radius = 2 + .8*np.cos(phi)
    xyz = np.stack((radius*np.cos(theta), radius*np.sin(theta), .8*np.sin(phi)), axis=-1)
    field = np.cos(3*theta)*np.cos(phi)

    # Wrap both index directions so neighboring quads share the seam vertices.
    index = np.arange(theta.size).reshape(theta.shape)
    next_theta = np.roll(index, -1, axis=0)
    next_phi = np.roll(index, -1, axis=1)
    quads = np.column_stack((
        index.ravel(), next_theta.ravel(),
        np.roll(next_theta, -1, axis=1).ravel(), next_phi.ravel(),
    ))
    triangles = np.vstack((quads[:, [0, 1, 2]], quads[:, [0, 2, 3]]))
    normals = np.stack((np.cos(phi)*np.cos(theta), np.cos(phi)*np.sin(theta), np.sin(phi)), axis=-1)

    fig, ax = plt.subplots(figsize=(8.8, 6.25), dpi=175, layout="constrained",
                           subplot_kw={"projection": "vtk3d", "antialiasing": antialiasing})
    fig.get_layout_engine().set(h_pad=.15, w_pad=.10)
    handle = ax.plot_mesh(xyz.reshape(-1, 3), triangles, values=field.ravel(),
                          lighting="gouraud", ambient=.62, diffuse=.41, specular=.09,
                          vmin=-1, vmax=1)
    handle.data.GetPointData().SetNormals(numpy_to_vtk(normals.reshape(-1, 3), deep=True))
    mpl3d_vtk.ax_setting(ax, (-3, 3), (-3, 3), (-1, 1))
    ax.set(xlabel=r"$x$", ylabel=r"$y$", zlabel=r"$z$")
    fig.suptitle(r"$f(\theta,\phi)=\cos(3\theta)\cos\phi$", fontsize=21)
    fig.colorbar(handle, ax=ax, label=r"$f(\theta,\phi)$",
                 ticks=[-1, -.5, 0, .5, 1], shrink=.64, fraction=.043, pad=.125)
    try:
        fig.savefig(destination, dpi=fig.dpi)
    finally:
        ax.remove()
        plt.close(fig)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, nargs="?", default=Path("closed_surface_trisurf.png"))
    parser.add_argument("--antialiasing", type=int, choices=(1,2,3,4), default=2)
    args = parser.parse_args()
    main(args.output, args.antialiasing)
