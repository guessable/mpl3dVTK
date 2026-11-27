"""Opt-in styles for Matplotlib figures and 3D axes."""

import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D


_AXIS_COLOR = "0.1294"
_AXIS_LINEWIDTH = .5
_GRID_COLOR = mpl.colors.to_rgba(_AXIS_COLOR, .15)
_TICK_LABEL_SIZE = 10
_AXIS_LABEL_SIZE = 11
# Seven colors from Paul Tol's dark palette for use on a white background.
# https://sronpersonalpages.nl/~pault/
_SERIES_COLORS = ("#4477BB", "#CC4466", "#117788", "#775500", "#882288", "#228833", "#444444")


def plot_rc(
    grid=False, tick_direction="in", tick_right=False, tick_top=False,
    save_dpi=300, save_bbox="tight", save_pad_inches=.05, font_family="serif",
    font_serif=("Arial", "Helvetica", "DejaVu Sans"), *, grid_3d=True,
):
    """Apply MATLAB-inspired figure defaults and a seven-color series cycle.

    Call before creating the figure. Axis labels and titles are 11 pt,
    tick labels are 10 pt, and legends are 9 pt. Titles use bold weight.
    Use a Matplotlib `rc_context` to limit the changes to one figure and
    `ax_setting` to apply the orthographic view and outward ticks to 3D axes.

    Parameters
    ----------
    grid : bool, default False
        Show the major grid on 2D axes.
    tick_direction : {"in", "out"}, default "in"
        Direction of the 2D tick marks.
    tick_right, tick_top : bool, default False
        Add ticks and tick labels on the right Y or top X side.
    save_dpi : float, default 300
        Default output resolution in dots per inch.
    save_bbox : {"tight", "standard"}, default "tight"
        Crop to the artists or export the whole figure canvas.
    save_pad_inches : float, default 0.05
        Padding in inches around a tight export.
    font_family : str, default "serif"
        Matplotlib font family passed to `my_mpl_style.plot_rc`.
    font_serif : sequence of str
        Font candidates used with the serif family. The default is
        ``("Arial", "Helvetica", "DejaVu Sans")``.
    grid_3d : bool, default True
        Show the grid on 3D axes.

    Returns
    -------
    None
        Update Matplotlib's `rcParams` in place.
    """
    from my_mpl_style import plot_rc as base_plot_rc

    base_plot_rc(
        grid=grid, tick_direction=tick_direction, tick_right=tick_right, tick_top=tick_top,
        save_dpi=save_dpi, save_bbox=save_bbox, save_pad_inches=save_pad_inches,
        font_family=font_family, font_serif=font_serif,
    )
    mpl.rcParams.update({
        "font.size": _TICK_LABEL_SIZE,
        "font.weight": "normal",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": _AXIS_COLOR,
        "axes.linewidth": _AXIS_LINEWIDTH,
        "axes.axisbelow": True,
        "axes.grid.axis": "both",
        "axes.grid.which": "major",
        "axes.labelcolor": _AXIS_COLOR,
        "axes.labelsize": _AXIS_LABEL_SIZE,
        "axes.labelweight": "normal",
        "axes.spines.bottom": True,
        "axes.spines.left": True,
        "axes.spines.top": True,
        "axes.spines.right": True,
        "axes.titlesize": _AXIS_LABEL_SIZE,
        "axes.titleweight": "bold",
        "axes.prop_cycle": mpl.cycler(color=_SERIES_COLORS),
        "grid.color": _GRID_COLOR,
        "grid.alpha": _GRID_COLOR[-1],
        "grid.linewidth": _AXIS_LINEWIDTH,
        "grid.linestyle": "-",
        "axes3d.grid": bool(grid_3d),
        "axes3d.xaxis.panecolor": "none",
        "axes3d.yaxis.panecolor": "none",
        "axes3d.zaxis.panecolor": "none",
        "legend.fontsize": 9,
        "legend.loc": "upper right",
        "legend.fancybox": False,
        "legend.facecolor": "white",
        "legend.edgecolor": _AXIS_COLOR,
        "legend.linewidth": _AXIS_LINEWIDTH,
        "legend.framealpha": 1,
        "legend.frameon": True,
        "xtick.bottom": True,
        "xtick.labelbottom": True,
        "xtick.top": bool(tick_top),
        "xtick.labeltop": bool(tick_top),
        "ytick.left": True,
        "ytick.labelleft": True,
        "ytick.right": bool(tick_right),
        "ytick.labelright": bool(tick_right),
    })
    for axis in ("xtick", "ytick"):
        mpl.rcParams.update({
            f"{axis}.color": _AXIS_COLOR,
            f"{axis}.labelcolor": _AXIS_COLOR,
            f"{axis}.labelsize": _TICK_LABEL_SIZE,
            f"{axis}.major.size": 3.5,
            f"{axis}.major.width": _AXIS_LINEWIDTH,
            f"{axis}.minor.visible": False,
            f"{axis}.minor.size": 1.75,
            f"{axis}.minor.width": _AXIS_LINEWIDTH,
        })


def ax_setting(
    ax=None, xlim=None, ylim=None, zlim=None, *,
    xticks=None, yticks=None, zticks=None, aspect="equal", box_aspect=None,
    xticks_pad=-5, yticks_pad=-5, zticks_pad=0, box_on=False,
    xtick_length=.025, ytick_length=.025, ztick_length=.025,
):
    """Apply an orthographic view, light grid, and projected ticks to a 3D axes.

    Use the MATLAB light theme's dark gray for the axes. Tick labels use
    10-point text and axis labels use 11-point text, both with normal weight.

    Parameters
    ----------
    ax : Axes3D or None, default None
        A Matplotlib ``3d`` or ``vtk3d`` axes. Use the current axes if omitted.
    xlim, ylim, zlim : pair of float or None, default None
        Limits in data units. Use the current limits and autoscaling mode
        for an axis when its limits are omitted.
    xticks, yticks, zticks : array_like or None, default None
        Tick locations in data units. Use the existing locator for an axis
        when its ticks are omitted.
    aspect : {"auto", "equal"}, default "equal"
        Automatic or equal data-unit proportions.
    box_aspect : triple of float or None, default None
        Relative XYZ box lengths. Supply a triple to override the proportions
        set by `aspect`.
    xticks_pad, yticks_pad : float, default -5
        X and Y tick-label padding in points.
    zticks_pad : float, default 0
        Adjust the Z tick-label gap, which is ``max(0, 2 + zticks_pad)`` points.
    box_on : bool, default False
        Draw the back pane outlines in gray by default. Use `True` to match
        their color to the axis lines.
    xtick_length, ytick_length, ztick_length : float, default 0.025
        Non-negative outward tick lengths as fractions of the longest
        projected axis.

    Returns
    -------
    None
        Modify the axes in place.

    Raises
    ------
    TypeError
        If the selected axes is two-dimensional or is not a Matplotlib 3D axes.
    ValueError
        If no current axes exists or a supplied value is invalid.
    """
    if ax is None:
        from matplotlib import pyplot as plt

        if not plt.get_fignums() or not plt.gcf().axes:
            raise ValueError("ax_setting() requires an existing 3D axes")
        ax = plt.gca()
    if not isinstance(ax, Axes3D):
        raise TypeError("ax must be a Matplotlib 3D axes")

    from my_mpl_style import ax_setting3D

    bounds = (xlim, ylim, zlim)
    limits = [getattr(ax, f"get_{name}lim")() if pair is None else pair
              for name, pair in zip("xyz", bounds)]
    # The upstream helper applies manual limits on all three axes.
    autoscale = {name: getattr(ax, f"get_autoscale{name}_on")()
                 for name, pair in zip("xyz", bounds) if pair is None}
    try:
        ax_setting3D(
            ax, *limits, xticks=xticks, yticks=yticks, zticks=zticks,
            aspect=aspect, box_aspect=box_aspect,
            xticks_pad=xticks_pad, yticks_pad=yticks_pad, zticks_pad=zticks_pad,
            box_on=box_on, xtick_length=xtick_length, ytick_length=ytick_length,
            ztick_length=ztick_length,
        )
    finally:
        for name, enabled in autoscale.items():
            getattr(ax, f"set_autoscale{name}_on")(enabled)

    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.line.set_color(_AXIS_COLOR)
        axis.line.set_linewidth(_AXIS_LINEWIDTH)
        axis.pane.set_linewidth(_AXIS_LINEWIDTH)
        if box_on:
            axis.pane.set_edgecolor(_AXIS_COLOR)
        # mplot3d reads these per-axis settings when it draws the ticks and grid.
        axis._axinfo["tick"]["linewidth"].update({True: _AXIS_LINEWIDTH, False: _AXIS_LINEWIDTH})
        axis._axinfo["grid"].update(color=_GRID_COLOR, linewidth=_AXIS_LINEWIDTH, linestyle="-")
        axis.set_tick_params(which="both", colors=_AXIS_COLOR, labelsize=_TICK_LABEL_SIZE)
        axis.label.set(color=_AXIS_COLOR, fontsize=_AXIS_LABEL_SIZE, fontweight="normal")
        axis.get_offset_text().set(color=_AXIS_COLOR, fontsize=_TICK_LABEL_SIZE, fontweight="normal")
        # Matplotlib copies label properties from the first tick when adding ticks.
        for tick in (*axis.majorTicks, *axis.minorTicks):
            tick.label1.set_fontweight("normal")
            tick.label2.set_fontweight("normal")
