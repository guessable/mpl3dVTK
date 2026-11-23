"""Render the zero level of independent, uniform random scalar samples."""
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import mpl3d_vtk  # Registers the vtk3d projection.


def main(destination, n=19, seed=42):
    coords = np.linspace(-1,1,n)
    values = np.random.default_rng(seed).uniform(-1,1,size=(n,n,n))
    fig,ax = plt.subplots(figsize=(8.2,6.8),dpi=175,layout="constrained",
                          subplot_kw={"projection":"vtk3d"})
    fig.get_layout_engine().set(h_pad=.15,w_pad=.16)
    _,_,z = np.meshgrid(coords,coords,coords,sparse=True)
    h = ax.plot_isosurface(values, coordinates=(coords, coords, coords), level=0,
                           color_values=np.broadcast_to(z, values.shape), vmin=-1, vmax=1,
                           ambient=.48, diffuse=.6, specular=.07)
    ax.set(xlabel="$x$",ylabel="$y$",zlabel="$z$")
    fig.suptitle("plot_isosurface", fontsize=19, fontfamily="monospace")
    ax.set_title(f"Random zero isosurface · {n}³ samples · seed {seed}", fontsize=12)
    fig.colorbar(h,ax=ax,label="$z$",ticks=[-1,-.5,0,.5,1],shrink=.64,pad=.07,fraction=.041)
    fig.savefig(destination)
    print(f"{n}^3 samples, seed {seed}, {h.data.GetNumberOfPolys()} triangles")
    ax.remove()
    plt.close(fig)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv)>1 else Path("random_isosurface.png"))
