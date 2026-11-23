import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import mpl3d_vtk as m


def test_surface_chart_geometry():
    fig, ax = plt.subplots(subplot_kw={"projection": "vtk3d"})
    t = np.linspace(-2, 2, 12)
    x, y = np.meshgrid(t,t)
    z = x*x-y*y
    faces = np.array([[0,1,2]])
    verts = np.array([[0,0,0],[1,0,0],[1,1,1]])
    calls = [
        lambda: m.surf(ax,z,"FaceColor","interp"),
        lambda: m.surface(ax,x,y,z),
        lambda: m.surfl(ax,x,y,z),
        lambda: m.surfnorm(ax,x,y,z),
        lambda: m.mesh(ax,z),
        lambda: m.meshc(ax,z),
        lambda: m.meshz(ax,z),
        lambda: m.surfc(ax,z),
        lambda: m.waterfall(ax,z),
        lambda: m.ribbon(ax,z[:,:2]),
        lambda: m.contour3(ax,z,[-1,1]),
        lambda: m.pcolor(ax,z),
        lambda: m.fsurf(ax,lambda x,y:x*x+y*y),
        lambda: m.fmesh(ax,lambda x,y:x*y),
        lambda: m.fimplicit3(ax,lambda x,y,z:x*x+y*y+z*z-1,(-2,2),samples=15),
        lambda: m.patch(ax,m.surf2patch(z,triangles=True)),
        lambda: m.fill3(ax,*verts.T),
        lambda: m.trisurf(ax,faces,*verts.T),
        lambda: m.trimesh(ax,faces,*verts.T),
        lambda: m.tetramesh(ax,[[0,1,2,3]],np.vstack((verts,[0,0,1]))),
        lambda: m.plot3(ax,t,np.sin(t),np.cos(t)),
        lambda: m.fplot3(ax,np.sin,np.cos,lambda t:t),
        lambda: m.scatter3(ax,t,np.sin(t),np.cos(t),[8]*12,t),
        lambda: m.stem3(ax,t),
        lambda: m.bubblechart3(ax,t,t,t,np.abs(t)),
        lambda: m.swarmchart3(ax,np.ones_like(t),t,t),
        lambda: m.bar3(ax,z[:3,:2]),
        lambda: m.bar3h(ax,z[:3,:2]),
        lambda: m.histogram2(ax,x.ravel(),y.ravel()),
        lambda: m.pie3(ax,[.2,.3,.5]),
        lambda: m.comet3(ax,t,t,t).set_frame(4),
    ]
    try:
        for draw in calls:
            ax.clear()
            draw()
            assert ax.handles
            assert any(h.data.GetNumberOfPoints() for h in ax.handles)
            fig.canvas.draw()
    finally:
        m.close(fig)


def test_volume_and_streamline_geometry():
    fig, ax = plt.subplots(subplot_kw={"projection": "vtk3d"})
    xyz = [np.linspace(-2,2,n) for n in (9,7,11)]
    x,y,z = np.meshgrid(*xyz)
    v = x*x+y*y+z*z
    u = np.ones_like(x)
    w = np.zeros_like(x)
    field = (*xyz,u,w,w)
    seeds = ([0],[0],[0])
    lines = m.stream3(*field,*seeds)
    assert len(lines) == 1
    np.testing.assert_allclose(lines[0][:,1:],0,atol=1e-6)
    np.testing.assert_allclose(m.divergence(*field),0,atol=1e-10)
    np.testing.assert_allclose(m.curl(*field),0,atol=1e-10)
    iso = m.isosurface(ax,*xyz,v,1)
    assert len(iso.faces)
    n = m.isonormals(*xyz,v,iso)
    assert np.isfinite(n).all()
    c = m.isocolors(*xyz,x,iso)
    np.testing.assert_allclose(c,iso.vertices[:,0],atol=1e-6)
    assert m.reducevolume(*xyz,v,2)[-1].shape == (4,5,6)
    assert m.subvolume(*xyz,v,[-1,1,-1,1,-1,1])[-1].shape == (3,5,5)
    assert m.smooth3(v).shape == v.shape
    assert len(m.reducepatch(iso,.5)["faces"]) < len(iso.faces)
    assert len(m.shrinkfaces(iso,.4)["faces"]) == len(iso.faces)
    calls = [
        lambda: m.isocaps(ax,*xyz,v,5),
        lambda: m.contourslice(ax,*xyz,v,[],[],[0],[1,3]),
        lambda: m.coneplot(ax,*field,*seeds),
        lambda: m.streamline(ax,lines),
        lambda: m.streamtube(ax,*field,*seeds),
        lambda: m.streamribbon(ax,lines),
        lambda: m.streamslice(ax,*field,[],[],[0]),
        lambda: m.streamparticles(ax,lines).set_frame(4),
    ]
    try:
        for draw in calls:
            ax.clear()
            draw()
            assert any(h.data.GetNumberOfPoints() for h in ax.handles)
            fig.canvas.draw()
    finally:
        m.close(fig)
