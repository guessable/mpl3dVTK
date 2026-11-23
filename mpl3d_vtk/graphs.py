"""VTK graph layout and drawing on a Matplotlib 3-D axes."""
from operator import index

import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy

from ._geometry import cells, numeric, output, poly
from .scene import Graphic


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


def plot_graph(self, edges, *, positions=None, node_count=None, directed=False,
               show_arrows=None, seed=0, node_labels=None, node_color="#296c9c",
               edge_color="#617a8d", node_size=49, **style):
    """Draw zero-based edges using explicit node positions or a force layout."""
    edges = np.asarray(edges)
    if edges.shape == (0,):
        edges = np.empty((0, 2), dtype=int)
    if edges.ndim != 2 or edges.shape[1] != 2 or not np.issubdtype(edges.dtype, np.integer):
        raise ValueError("edges must be an (n, 2) integer array")
    if edges.size and edges.min() < 0:
        raise ValueError("edge indices must be nonnegative")
    minimum = int(edges.max()) + 1 if edges.size else 0
    if positions is None:
        count = minimum if node_count is None else index(node_count)
        if count < max(minimum, 1):
            raise ValueError("node_count must include all edge endpoints")
        if count == 1 or not edges.size:
            angle = np.linspace(0, 2 * np.pi, count, endpoint=False)
            positions = np.column_stack((np.cos(angle), np.sin(angle), np.zeros(count)))
        else:
            positions = _force_layout(edges, count, directed, seed)
    elif node_count is not None and len(positions) != node_count:
        raise ValueError("node_count must match the number of positions")
    xyz = numeric(positions)
    if xyz.ndim != 2 or xyz.shape[1] != 3 or len(xyz) < minimum or not np.isfinite(xyz).all():
        raise ValueError("positions must be a finite (n, 3) array containing all endpoints")
    if node_labels is not None and len(node_labels) != len(xyz):
        raise ValueError("supply one label per node")

    data = poly(xyz)
    data.SetLines(cells(edges))
    graph = Graphic(self, data, **{"color": edge_color, **style})
    graph._companions = []
    try:
        graph.nodes = self.scatter(*xyz.T, s=node_size, c=node_color)
        graph._companions.append(graph.nodes)
        if edges.size and (directed if show_arrows is None else show_arrows):
            start, end = xyz[edges[:, 0]], xyz[edges[:, 1]]
            delta = end - start
            graph.arrows = self.quiver(*(start + .7 * delta).T, *delta.T, length=.22, color=edge_color)
            graph._companions.append(graph.arrows)
        if node_labels is not None:
            graph.annotations.extend(self.text(*point, str(label), fontsize=8, va="bottom", ha="left")
                                     for point, label in zip(xyz, node_labels))
        graph.set_visible(graph.get_visible())
    except Exception:
        graph.remove()
        raise
    return graph
