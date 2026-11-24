"""Opt-in styling for Matplotlib 3D axes."""

from mpl_toolkits.mplot3d import Axes3D


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
