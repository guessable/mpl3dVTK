"""Render the zero level of independent, uniform random scalar samples."""
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import mpl3d_vtk as m


def main(destination, n=19, seed=42):
    coords = np.linspace(-1,1,n)
    values = np.random.default_rng(seed).uniform(-1,1,size=(n,n,n))
    fig,ax = plt.subplots(figsize=(8.2,6.8),dpi=175,layout="constrained",
                          subplot_kw={"projection":"vtk3d"})
    fig.get_layout_engine().set(h_pad=.15,w_pad=.16)
    _,_,z = np.meshgrid(coords,coords,coords,sparse=True)
    h = m.isosurface(ax,coords,coords,coords,values,0,
                     colors=np.broadcast_to(z,values.shape),cmap="viridis",clim=(-1,1),
                     AmbientStrength=.48,DiffuseStrength=.6,SpecularStrength=.07)
    ax.set(xlim=(-1,1),ylim=(-1,1),zlim=(-1,1),xlabel="$x$",ylabel="$y$",zlabel="$z$")
    ax.set(xticks=[-1,-.5,0,.5,1],yticks=[-.5,0,.5,1],zticks=[-1,-.5,0,.5,1])
    ax.set_box_aspect((1,1,1),zoom=.95)
    ax.view_init(elev=29,azim=-60)
    ax.set_title(r"Zero isosurface  $V(x,y,z)=0$",fontsize=19,pad=10)
    fig.colorbar(h,ax=ax,label="$z$",ticks=[-1,-.5,0,.5,1],shrink=.64,pad=.07,fraction=.041)
    fig.savefig(destination,facecolor="white")
    print(f"{n}^3 samples, seed {seed}, {h.data.GetNumberOfPolys()} triangles")
    m.close(fig)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv)>1 else Path("random_isosurface.png"))
