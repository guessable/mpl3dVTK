"""Opt-in styles for Matplotlib figures and 3D axes."""

import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D


def plot_rc(
    grid=False, tick_direction="out", tick_right=False, tick_top=False,
    save_dpi=300, save_bbox="tight", save_pad_inches=.05, font_family="serif",
    font_serif=("Arial", "Helvetica", "DejaVu Sans"), *, grid_3d=True,
):
    """Apply my-mpl-style defaults with custom legends and 3D axes.

    Call before creating the figure. Use a Matplotlib `rc_context` to limit
    the changes to one figure.

    Parameters
    ----------
    grid : bool, default False
        Show the major grid on 2D axes.
    tick_direction : {"in", "out"}, default "out"
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
        "axes3d.grid": bool(grid_3d),
        "axes3d.xaxis.panecolor": "none",
        "axes3d.yaxis.panecolor": "none",
        "axes3d.zaxis.panecolor": "none",
        "legend.frameon": True,
        "legend.fancybox": False,
        "legend.edgecolor": "0.15",
        "legend.framealpha": 1,
    })


def ax_setting(
    ax=None, xlim=None, ylim=None, zlim=None, *,
    xticks=None, yticks=None, zticks=None, aspect="equal", box_aspect=None,
    xticks_pad=-5, yticks_pad=-5, zticks_pad=0, box_on=False,
    xtick_length=.02, ytick_length=.02, ztick_length=.02,
):
    """Apply an orthographic view and projected ticks to a 3D axes.

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
        Use the axis line colors for the pane outlines. The default is gray.
    xtick_length, ytick_length, ztick_length : float, default 0.02
        Non-negative lengths as fractions of the longest projected axis.

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
