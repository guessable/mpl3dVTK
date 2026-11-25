"""Scientific 3D graphics powered by VTK and Matplotlib.

Importing this package registers the Matplotlib projection ``vtk3d``.
"""

from ._axes import VtkAxes
from ._axes_style import ax_setting, plot_rc
from .scene import Graphic
from .vectors import trace_streamlines
from .volumes import extract_isosurface

__all__ = ["Graphic", "VtkAxes", "ax_setting", "extract_isosurface", "plot_rc", "trace_streamlines"]
__version__ = "0.5.7"
