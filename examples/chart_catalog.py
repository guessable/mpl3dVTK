"""A visual index of twelve chart types using the package's VTK plotters."""
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import mpl3d_vtk  # Registers the vtk3d projection.


def main(destination):
    fig,axes = plt.subplots(4,3,figsize=(12.8,15),dpi=155,layout="constrained",
                            subplot_kw={"projection":"vtk3d"})
    fig.get_layout_engine().set(h_pad=.09,w_pad=.08)
    t = np.linspace(-3,3,32)
    x,y = np.meshgrid(t,t)
    z = np.exp(-.22 * (x*x + y*y)) * np.sin(2*x) * np.cos(2*y)
    s = np.linspace(-1.4,1.4,45)
    X,Y,Z = np.meshgrid(s,s,s,sparse=True)
    vol = X**2+1.5*Y**2+.7*Z**2
    u = np.linspace(-1,1,7)
    qx,qy,qz = np.meshgrid(u,u,[-.6,0,.6])
    angle = np.linspace(0,2*np.pi,24,endpoint=False)
    tx = np.r_[0,np.cos(angle),.55*np.cos(angle)]
    ty = np.r_[0,np.sin(angle),.55*np.sin(angle)]
    tz = 1.2*np.exp(-2*(tx*tx+ty*ty))+.22*(tx-ty)
    from matplotlib.tri import Triangulation
    tri = Triangulation(tx,ty).triangles
    rng = np.random.default_rng(7)
    p = rng.normal(size=(140,3))
    bars = np.array([[2,4,3], [4,1,3], [3,5,2], [2,3,4]])
    by, bx = np.indices(bars.shape)
    line = np.linspace(0, 4*np.pi, 320)
    plots = [
        ("plot_surface", lambda ax: ax.plot_surface(x, y, z, cmap="viridis")),
        ("surface with lighting", lambda ax: ax.plot_surface(x, y, z, color="#4f93ba", shade=True)),
        ("plot_wireframe", lambda ax: ax.plot_wireframe(x, y, z, rstride=2, cstride=2)),
        ("surface + contour", lambda ax: (
            ax.plot_surface(x, y, z, cmap="viridis", alpha=.75),
            ax.contour(x, y, z, offset=-1, color="black"),
        )),
        ("plot", lambda ax: ax.plot(np.cos(line), np.sin(line), line / (2*np.pi), linewidth=2)),
        ("stem", lambda ax: ax.stem(t, np.zeros_like(t), np.cos(t))),
        ("plot_trisurf", lambda ax: ax.plot_trisurf(tx, ty, tz, triangles=tri, cmap="viridis")),
        ("contour", lambda ax: ax.contour(x, y, z, levels=11, linewidth=1.8)),
        ("bar3d", lambda ax: ax.bar3d(bx, by, 0, .75, .75, bars, cmap="viridis")),
        ("scatter", lambda ax: ax.scatter(*p.T, s=26, c=p[:,2])),
        ("quiver", lambda ax: ax.quiver(qx, qy, qz, -qy, qx, .35, length=.22)),
        ("plot_volume_slices", lambda ax: ax.plot_volume_slices(
            vol, coordinates=(s, s, s), x=0, y=.5, z=-.6, alpha=.92
        )),
    ]
    for ax,(name,draw) in zip(axes.flat,plots):
        draw(ax)
        ax.set_title(name,loc="left",fontfamily="monospace",fontweight="bold",fontsize=15,pad=9)
    fig.savefig(destination)
    for ax in axes.flat:
        ax.remove()
    plt.close(fig)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv)>1 else Path("chart_catalog.png"))
