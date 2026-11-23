"""A visual index of twelve chart types using the package's VTK plotters."""
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np

import mpl3d_vtk as m


def main(destination):
    fig,axes = plt.subplots(4,3,figsize=(12.8,15),dpi=155,layout="constrained",
                            subplot_kw={"projection":"vtk3d"})
    fig.get_layout_engine().set(h_pad=.09,w_pad=.08)
    t = np.linspace(-3,3,32)
    x,y = np.meshgrid(t,t)
    z = m.peaks(x,y)
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
    plots = [
        ("surf",lambda a:m.surf(a,x,y,z,FaceColor="interp",EdgeColor="none",cmap="viridis")),
        ("surfl",lambda a:m.surfl(a,x,y,z,cmap="bone")),
        ("mesh",lambda a:m.mesh(a,x[::2,::2],y[::2,::2],z[::2,::2],cmap="viridis")),
        ("surfc",lambda a:m.surfc(a,x,y,z,FaceColor="interp",EdgeColor="none",cmap="coolwarm")),
        ("waterfall",lambda a:m.waterfall(a,x[::3],y[::3],z[::3],cmap="plasma",LineWidth=1.7)),
        ("ribbon",lambda a:m.ribbon(a,t,np.sin(t[:,None]*[.9,1.3,1.7,2.1])+[0,.4,.8,1.2],
                                     FaceColor="interp",EdgeColor="none",cmap="cividis")),
        ("trisurf",lambda a:m.trisurf(a,tri,tx,ty,tz,EdgeColor="#334653",cmap="viridis")),
        ("contour3",lambda a:m.contour3(a,x,y,z,np.linspace(-5,7,11),cmap="turbo",LineWidth=1.8)),
        ("bar3",lambda a:m.bar3(a,[[2,4,3],[4,1,3],[3,5,2],[2,3,4]],cmap="Blues",EdgeColor="#5e7290")),
        ("scatter3",lambda a:m.scatter3(a,*p.T,26,p[:,2],"filled",cmap="plasma")),
        ("quiver3",lambda a:m.quiver3(a,qx,qy,qz,-qy,qx,.35*np.ones_like(qx),.95,cmap="viridis")),
        ("slice",lambda a:m.slice(a,s,s,s,vol,[0],[.5],[-.6],cmap="magma",FaceAlpha=.92)),
    ]
    for ax,(name,draw) in zip(axes.flat,plots):
        draw(ax)
        ax.view_init(elev=31,azim=-57)
        ax.set_box_aspect((1,1,.74),zoom=.94)
        ax.set_title(name,loc="left",fontfamily="monospace",fontweight="bold",fontsize=15,pad=2)
        for axis in (ax.xaxis,ax.yaxis,ax.zaxis):
            axis.set_major_locator(MaxNLocator(4,prune="both"))
            axis.pane.set_facecolor("#f2f5f8")
        ax.tick_params(labelsize=7,pad=-1)
    fig.savefig(destination,facecolor="white")
    m.close(fig)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv)>1 else Path("chart_catalog.png"))
