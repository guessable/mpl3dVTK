"""VTK graph layout and drawing on a Matplotlib 3-D axes."""
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy

from ._geometry import cells, numeric, output, poly
from .charts import scatter3
from .scene import Graphic, chart
from .vectors import quiver3


def _force_layout(edges, count, directed, seed):
    graph = vtk.vtkMutableDirectedGraph() if directed else vtk.vtkMutableUndirectedGraph()
    for _ in range(count):
        graph.AddVertex()
    for a,b in edges:
        graph.AddEdge(int(a),int(b))
    strategy = vtk.vtkForceDirectedLayoutStrategy()
    strategy.ThreeDimensionalLayoutOn()
    strategy.SetRandomSeed(int(seed))
    strategy.SetMaxNumberOfIterations(180)
    strategy.SetIterationsPerLayout(180)
    layout = vtk.vtkGraphLayout()
    layout.SetLayoutStrategy(strategy)
    return vtk_to_numpy(output(layout,graph).GetPoints().GetData()).copy()


@chart
def graphplot(edges, xyz=None, *, ax, xdata=None, ydata=None, zdata=None, layout="force3",
              node_count=None, directed=False, show_arrows=None, index_base=0, seed=0,
              node_label=None, node_color="#296c9c", edge_color="#617a8d", markersize=7,
              **kwargs):
    """Draw an edge list with specified 3-D positions or a VTK force layout."""
    edge_color = kwargs.pop("edgecolor",edge_color)
    if isinstance(edges,dict):
        xyz = edges.get("points",xyz)
        directed = edges.get("directed",directed)
        edges = edges["edges"]
    e = np.asarray(edges)
    if not e.size and e.ndim == 1:
        e = np.empty((0,2),dtype=int)
    if e.ndim != 2 or e.shape[1] != 2 or not np.issubdtype(e.dtype,np.integer):
        raise ValueError("edges must be an (n, 2) integer array")
    if index_base not in (0,1):
        raise ValueError("index_base must be 0 or 1")
    e = e-index_base
    min_count = int(e.max())+1 if len(e) else 0
    if len(e) and e.min() < 0:
        raise ValueError("edges contain a negative index")
    if any(a is not None for a in (xdata,ydata,zdata)):
        if xdata is None or ydata is None or xyz is not None:
            raise ValueError("provide XData and YData together, or use xyz")
        xyz = np.column_stack(np.broadcast_arrays(xdata,ydata,0 if zdata is None else zdata))
    if xyz is None:
        if layout != "force3":
            raise ValueError("layout must be force3 when coordinates are omitted")
        count = int(node_count) if node_count is not None else min_count
        if count < max(min_count,1):
            raise ValueError("node_count must include all edge endpoints")
        if count == 1 or not len(e):
            angle = np.linspace(0,2*np.pi,count,endpoint=False)
            xyz = np.column_stack((np.cos(angle),np.sin(angle),np.zeros(count)))
        else:
            xyz = _force_layout(e,count,directed,seed)
    xyz = numeric(xyz)
    if xyz.ndim != 2 or xyz.shape[1] != 3 or len(xyz) < min_count or not np.isfinite(xyz).all():
        raise ValueError("node coordinates must be an (n, 3) finite array containing all endpoints")
    if node_label is not None and len(node_label) != len(xyz):
        raise ValueError("supply one NodeLabel per node")
    data = poly(xyz)
    data.SetLines(cells(e))
    graph = Graphic(ax,data,**{"color":edge_color,**kwargs})
    graph.nodes = scatter3(ax,*xyz.T,float(markersize)**2,node_color)
    graph._companions = [graph.nodes]
    if len(e) and ((show_arrows is None and directed) or show_arrows in (True,"on")):
        p0,p1 = xyz[e[:,0]],xyz[e[:,1]]
        delta = p1-p0
        graph.arrows = quiver3(ax,*(p0+.7*delta).T,*(.22*delta).T,0,color=edge_color)
        graph._companions.append(graph.arrows)
    graph.set_visible(graph.get_visible())
    if node_label is not None:
        for p,label in zip(xyz,node_label):
            graph.annotations.append(ax.text(*p,str(label),fontsize=8,va="bottom",ha="left"))
    return graph


def plot(*args, **kwargs):
    """MATLAB graph plot spelling for a graph given by its edge list."""
    return graphplot(*args,**kwargs)
