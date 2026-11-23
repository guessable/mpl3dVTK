import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest
from vtk.util.numpy_support import vtk_to_numpy

import mpl3d_vtk as m


@pytest.fixture
def axes():
    fig, ax = plt.subplots(subplot_kw={"projection":"vtk3d"})
    yield ax
    m.close(fig)


def test_surface_properties_and_native_legend(axes):
    z = np.arange(9.).reshape(3,3)
    h = m.surf(axes,z,"FaceColor","interp","EdgeColor","none",
               CDataMapping="direct",cmap=np.eye(3),DisplayName="surface",
               FaceAlpha="interp",AlphaData=z/8,FaceLighting="gouraud")
    rgba = vtk_to_numpy(h.data.GetPointData().GetArray("display_rgba"))
    assert rgba[:,3].min() == 0 and rgba[:,3].max() == 255
    np.testing.assert_array_equal(rgba[1,:3],[255,0,0])
    assert h.data.GetPointData().GetNormals().GetNumberOfTuples() == z.size
    assert axes.legend().get_texts()[0].get_text() == "surface"
    m.set(h,"FaceColor","red",LineWidth=3)
    assert h.actor.GetProperty().GetLineWidth() == 3
    other = m.surface(axes,ZData=z+1,EdgeColor="none")
    assert axes.handles == [h,other]
    m.set(other,ZData=z+2)
    np.testing.assert_allclose(other.vertices[:,2],(z+2).ravel())
    axes.figure.canvas.draw()


def test_contour_matrix_and_ragged_patch(axes):
    x,y = np.meshgrid(np.linspace(-1,1,7),np.linspace(-1,1,5))
    matrix,h = m.contour3(axes,x,y,x,[-.5,.5],"r-",return_matrix=True)
    assert h.data.GetNumberOfLines() == 2
    i = 0
    while i < matrix.shape[1]:
        level,count = matrix[:,i]
        assert abs(level) == .5
        np.testing.assert_allclose(matrix[0,i+1:i+1+int(count)],level)
        i += int(count)+1
    v = [[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,-1,0]]
    p = m.patch(axes,"Faces",[[1,2,3,4],[1,2,5,np.nan]],"Vertices",v,index_base=1)
    assert [len(face) for face in p.faces] == [4,3]


def test_nonuniform_slice_and_flying_edges_colors(axes):
    x,y,z = [np.array(a,dtype=float) for a in ([0,1,2,4],[-1,0,1,3],[0,1,2,3,5])]
    X,Y,Z = np.meshgrid(x,y,z)
    values = X**3+2*Y-Z
    a,b = m.slice(axes,x,y,z,values,[1.3,1.7],[],[],"nearest")
    assert a.get_clim() == b.get_clim()
    np.testing.assert_allclose(a.get_array(), 1+2*a.vertices[:,1]-a.vertices[:,2],atol=1e-6)
    c, = m.slice(axes,x,y,z,values,[1.3],[],[],"cubic")
    np.testing.assert_allclose(c.get_array(),c.vertices[:,0]**3+2*c.vertices[:,1]-c.vertices[:,2],atol=1e-5)
    t = np.linspace(-1,1,7)
    X,Y,Z = np.meshgrid(t,t,t)
    g = m.isosurface_geometry(t,t,t,X+Y+Z,.2,X,"noshare")
    assert len(g["vertices"]) == 3*len(g["faces"])
    np.testing.assert_allclose(g["vertices"].sum(axis=1),.2,atol=1e-6)
    np.testing.assert_allclose(g["facevertexcdata"],g["vertices"][:,0],atol=1e-6)


def test_table_lines_animation_and_histogram(axes):
    t = np.arange(5.)
    h = m.plot3(axes,{"x":t,"y":2*t,"z":t**2},"x","y","z")
    np.testing.assert_allclose(h.vertices[:,2],t**2)
    lines = m.plot3(axes,np.stack([t,2*t]), t, t)
    assert len(lines) == 2
    a = m.animatedline(axes,MaximumNumPoints=3,Color="r")
    m.addpoints(a,t[:2],t[:2],t[:2])
    m.addpoints(a,t[2:],t[2:],t[2:])
    axes.figure.canvas.draw()
    np.testing.assert_array_equal(m.getpoints(a)[0],[2,3,4])
    m.clearpoints(a)
    assert not len(m.getpoints(a)[0])
    b = m.histogram2(axes,[.25,1.25],[.5,.5],
                     XBinEdges=[0,1,3],YBinEdges=[0,2],Normalization="pdf")
    np.testing.assert_allclose(b.values[:,0],[.25,.125])


def test_cones_and_streamline_overloads(axes):
    x,y,z = np.meshgrid(np.arange(1.,6.),np.arange(1.,5.),np.arange(1.,4.))
    u = np.ones_like(x)
    w = np.zeros_like(x)
    colored = m.coneplot(axes,x,y,z,u,w,w,[2.2],[2.],[2.],x,"nearest")
    np.testing.assert_allclose(colored.get_array(),[2.])
    q = m.quiver3(axes,[0,1],[1,1],[1,1],[1,1],[0,0],[0,0],0,"ro","filled",ShowArrowHead="off")
    assert q.markers.data.GetNumberOfPoints() == 2
    line, = m.stream2(u[:,:,0],w[:,:,0],2,2)
    np.testing.assert_allclose(line[:,1],2)
    assert m.streamline(axes,[line]).data.GetNumberOfPoints() > 0
    path = np.column_stack((line,np.zeros(len(line))))
    h = m.streamribbon(axes,[path],np.linspace(0,1,len(path)),.1)
    assert h.data.GetNumberOfPolys() == len(path)-1
    assert m.streamtube(axes,[path],.2,[1,12]).data.GetNumberOfCells() > 0
    axes.figure.canvas.draw()


def test_transparent_vtk_render_composites_with_matplotlib(axes):
    x,y = np.meshgrid([-1.,1.],[-1.,1.])
    m.surf(axes,x,y,np.zeros_like(x),FaceColor="red",FaceAlpha=.5,EdgeColor="none")
    axes.set_axis_off()
    axes.view_init(elev=85,azim=0)
    axes.figure.canvas.draw()
    frame = np.asarray(axes.figure.canvas.buffer_rgba())
    pixel = frame[frame.shape[0]//2,frame.shape[1]//2]
    np.testing.assert_allclose(pixel,[255,128,128,255],atol=2)


def test_point_cloud_transforms_and_volume(axes):
    p = np.random.default_rng(18).normal(size=(320,3))
    a,b = m.pcshowpair(axes,p,p+np.array([1.,0.,0.]),MarkerSize=3)
    assert len(a.vertices) == len(b.vertices) == len(p)
    q = [np.sqrt(.5),0,0,np.sqrt(.5)]
    frames = m.plotTransforms(axes,[[1,2,3]],q,FrameSize=.5)
    vtk_vec = vtk_to_numpy(frames[0].data.GetPointData().GetVectors())
    np.testing.assert_allclose(vtk_vec,[[0,.5,0]],atol=1e-10)
    h = m.alphashape(axes, p, 1.1)
    assert len(h.faces)
    t = np.linspace(-1,1,29)
    x,y,z = np.meshgrid(t,t,t,sparse=True)
    v = np.exp(-4*(x*x+y*y+z*z))
    volume = m.volshow(axes,v,coords=(t,t,t),Colormap="magma",AlphaMap=[0,.02,.6],
                       RenderingStyle="MaximumIntensityProjection")
    assert volume.actor.IsA("vtkVolume")
    axes.figure.colorbar(volume,ax=axes)
    axes.figure.canvas.draw()
    assert np.count_nonzero(axes._viewport_frame[...,3]) > 100
    assert len(axes.handles) == 1


def test_graph_plot_with_positions_and_force_layout(axes):
    from types import SimpleNamespace
    edges = [[0,1],[1,2],[2,3],[3,0],[0,2]]
    points = np.array([[0.,0.,0.],[1.,0.,1.],[1.,1.,0.],[0.,1.,1.]])
    graph = m.plot(axes,edges,XData=points[:,0],YData=points[:,1],ZData=points[:,2],
                   directed=True,NodeLabel=["A","B","C","D"])
    np.testing.assert_allclose(graph.vertices,points)
    assert graph.data.GetNumberOfLines() == len(edges)
    assert graph.arrows.data.GetNumberOfPoints() == len(edges)
    assert len(graph.annotations) == len(points)
    graph = m.graphplot(axes,edges,layout="force3")
    assert len(graph.vertices) == 4
    assert np.ptp(graph.vertices[:,2]) > 0
    obj = SimpleNamespace(Points=points,ConnectivityList=[[1,2,3,4]])
    tris = m.trisurf(axes,obj,index_base=1)
    assert tris.faces.shape == (4,3)
    tets = m.tetramesh(axes,obj,index_base=1)
    assert tets.faces.shape == (4,3)


def test_image_plane_with_scaled_and_indexed_color(axes):
    rgb = np.array([[[1.,0.,0.],[0.,1.,0.]],[[0.,0.,1.],[1.,1.,0.]]])
    h = m.image(axes,[0,1],[0,1],rgb,z=.4)
    assert h.data.GetNumberOfPolys() == 1
    np.testing.assert_allclose(h.vertices[:,2],.4)
    assert h.texture.GetInput().GetDimensions() == (2,2,1)
    axes.set_axis_off()
    axes.view_init(elev=88,azim=-88)
    axes.figure.canvas.draw()
    pixels = axes._viewport_frame.reshape(-1,4)
    for expected in ([255,0,0,255],[0,255,0,255],[0,0,255,255],[255,255,0,255]):
        assert np.any(np.all(pixels == expected,axis=1))
    s = m.imagesc(axes,[[0.,1.],[2.,3.]],[0.,3.],cmap="viridis")
    axes.figure.colorbar(s,ax=axes)
    s.set_cdata(np.ones((2,2)))
    np.testing.assert_allclose(s.get_array(),1.)
    np.testing.assert_allclose(s.get_clim(),[0.,3.])
    m.image(axes,np.array([[0,1],[1,1]],dtype=np.uint8),cmap=[[1,0,0],[0,1,0]])
    axes.figure.canvas.draw()
