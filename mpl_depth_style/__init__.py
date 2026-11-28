"""Scientific 3D graphics powered by VTK and Matplotlib.

Importing this package registers the Matplotlib projection ``vtk3d``.
"""

from ._axes import VtkAxes
from ._axes_style import ax3D_setting, plot_rc
from .scene import Graphic

__all__ = ["Graphic", "VtkAxes", "ax3D_setting", "plot_rc"]
