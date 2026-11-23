"""Render a reference gallery of VTK-specific axes methods."""
from argparse import ArgumentParser
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import mpl3d_vtk as m


def main(destination):
    fig, axes = plt.subplots(3, 3, figsize=(11, 10), layout="constrained",
                             subplot_kw={"projection": "vtk3d"})
    t = np.linspace(-1, 1, 29)
    x, y, z = np.meshgrid(t, t, t)
    values = x*x + y*y + z*z
    field = np.stack((-y, x, np.full_like(z, .18)), axis=-1)
    seeds = [[.3, 0, -.9], [.57, 0, -.9]]
    paths = m.trace_streamlines(field, seeds, coordinates=(t, t, t))
    rng = np.random.default_rng(5)
    cloud = rng.normal(size=(130, 3))
    image = np.sin(17*x[:, :, 0]) * np.cos(14*y[:, :, 0])
    edge_list = [[0, 1], [0, 2], [0, 3], [1, 2], [2, 3], [1, 3]]

    plots = [
        ("plot_isosurface", lambda ax: ax.plot_isosurface(values, coordinates=(t,t,t), level=.8)),
        ("plot_volume", lambda ax: ax.plot_volume(np.exp(-5*values), coordinates=(t,t,t), cmap="magma")),
        ("plot_slice_contours", lambda ax: ax.plot_slice_contours(values, coordinates=(t,t,t), z=[-.5,.5])),
        ("plot_streamlines", lambda ax: ax.plot_streamlines(paths, linewidth=2)),
        ("plot_streamtubes", lambda ax: ax.plot_streamtubes(paths, radius=.035)),
        ("plot_streamribbons", lambda ax: ax.plot_streamribbons(paths, width=.11)),
        ("plot_point_cloud", lambda ax: ax.plot_point_cloud(cloud, c=cloud[:, 2])),
        ("plot_graph", lambda ax: ax.plot_graph(edge_list, node_labels=list("ABCD"), directed=True)),
        ("plot_image_plane", lambda ax: ax.plot_image_plane(image, extent=(-1, 1, -1, 1), z=0)),
    ]
    try:
        for ax, (name, plot) in zip(axes.flat, plots):
            plot(ax)
            ax.set_title(name, fontfamily="monospace")
        fig.savefig(destination, dpi=150)
    finally:
        for ax in axes.flat:
            ax.remove()
        plt.close(fig)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", type=Path, default=Path("vtk_reference.png"))
    main(parser.parse_args().output)
