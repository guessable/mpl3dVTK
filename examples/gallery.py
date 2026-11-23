"""Render four VTK charts in a native Matplotlib figure."""
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np

import mpl3d_vtk as m


def _style(ax, title, elev, azim, aspect=(1,1,.75)):
    ax.view_init(elev=elev,azim=azim)
    ax.set_box_aspect(aspect,zoom=.91)
    ax.set(xlabel="$x$",ylabel="$y$",zlabel="$z$")
    ax.set_title(title,loc="left",fontsize=14,fontweight="bold",pad=2)
    for a in (ax.xaxis,ax.yaxis,ax.zaxis):
        a.set_major_locator(MaxNLocator(4))
        a.pane.set_facecolor("#f3f6f9")
        a.pane.set_edgecolor("#dae2eb")
    ax.tick_params(axis="both",labelsize=8,pad=-1,colors="#424f60")


def main(destination):
    fig, axs = plt.subplots(2,2,figsize=(11.5,9),dpi=170,layout="constrained",
                            subplot_kw={"projection":"vtk3d"})
    fig.get_layout_engine().set(h_pad=.15,w_pad=.18)
    fig.suptitle("3D scientific plots",x=.095,ha="left",fontsize=23,fontweight="bold")
    a,b,c,d = axs.ravel()

    t = np.linspace(-2,2,201)
    x,y = np.meshgrid(t,t)
    u = np.exp(x*np.sin(y))
    h = m.surf(a,x,y,u,FaceColor="interp",EdgeColor="none",cmap="viridis")
    a.set(xlim=(-2,2),ylim=(-2,2),zlim=(0,8))
    _style(a,r"Surface  $u=e^{xsin y}$",31,-58)
    a.set_zlabel("$u$")
    fig.colorbar(h,ax=a,shrink=.62,fraction=.04,pad=.08,ticks=[1,3,5,7])

    t = np.linspace(-1.5,1.5,61)
    xx,yy,zz = np.meshgrid(t,t,t,sparse=True)
    field = np.broadcast_to(xx**2+1.5*yy**2+.7*zz**2,(len(t),)*3)
    m.hold("on",ax=b)
    m.isosurface(b,t,t,t,field,1.2,FaceColor="#187ea5",FaceAlpha=.38)
    slices = m.slice(b,t,t,t,field,[],[],[-.3],cmap="magma",
                     FaceAlpha=.88,clim=(0,4.5))
    _style(b,"Isosurface and scalar slice",28,-57)
    b.set(xlim=(-1.5,1.5),ylim=(-1.5,1.5),zlim=(-1.5,1.5))
    fig.colorbar(slices[0],ax=b,shrink=.62,fraction=.04,pad=.08,ticks=[0,1.5,3,4.5])

    t = np.linspace(0,4*np.pi,450)
    m.hold("on",ax=c)
    m.plot3(c,np.cos(t),np.sin(t),t/np.pi,Color="#087f9c",LineWidth=2.2)
    m.plot3(c,-np.cos(t),-np.sin(t),t/np.pi,Color="#b85253",LineWidth=2.2)
    knots = np.linspace(0,4*np.pi,14)
    m.scatter3(c,np.cos(knots),np.sin(knots),knots/np.pi,36,"#087f9c","filled")
    m.scatter3(c,-np.cos(knots),-np.sin(knots),knots/np.pi,36,"#b85253","filled")
    _style(c,"3D lines and point markers",23,-56,aspect=(1,1,1.1))

    x0 = np.linspace(-1,1,31)
    zz0 = np.linspace(0,3,45)
    x,y,z = np.meshgrid(x0,x0,zz0)
    u,v,w = -y,x,np.full_like(z,.26)
    m.hold("on",ax=d)
    for radius,color in [(0.34,"#147d99"),(.65,"#dc8c3c"),(.85,"#8d559b")]:
        m.streamtube(d,x0,x0,zz0,u,v,w,[radius],[0],[.03],radius=.026,
                     sides=18,FaceColor=color)
    _style(d,"Stream tubes in a swirling field",26,-54,aspect=(1,1,1.1))
    d.set(xlim=(-1,1),ylim=(-1,1),zlim=(0,3))
    d.set_xticks([-1,-.5,0,.5])
    fig.savefig(destination,facecolor="white")
    m.close(fig)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv)>1 else Path("gallery.png"))
