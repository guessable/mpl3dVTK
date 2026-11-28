"""Measure construction time for the five vtk3d plotting methods."""
import argparse
import json
from pathlib import Path
import platform
from statistics import median
from time import perf_counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import vtk

import mpl_depth_style


def workloads(ax, data_dir):
    t = np.linspace(-2, 2, 600)
    x, y = np.meshgrid(t, t, sparse=True)
    heights = np.sin(x) * np.cos(y)

    with np.load(data_dir / "cheese.npz", allow_pickle=False) as data:
        a, b, c = data["vertices"].T
        faces = data["elements"]
    colors = a * np.sin(c) + b * np.sin(a ** 2)

    coords = np.linspace(-1, 1, 128)
    X, Y, Z = np.meshgrid(coords, coords, coords, sparse=True)
    volume = X ** 2 + Y ** 2 + Z ** 2
    volume_colors = X + Y + Z

    u = np.linspace(0, 8 * np.pi, 250_000)
    line = (np.cos(u), np.sin(u), u)
    points = np.random.default_rng(42).uniform(-1, 1, size=(3, 250_000))
    return {
        "plot_surface": lambda: ax.plot_surface(t, t, heights, cmap="viridis", lighting="gouraud"),
        "plot_trisurf": lambda: ax.plot_trisurf(a, b, c, triangles=faces, values=colors, cmap="viridis"),
        "plot_isosurface": lambda: ax.plot_isosurface(
            volume, level=.5, coordinates=(coords,) * 3, color_values=volume_colors, cmap="viridis"
        ),
        "plot": lambda: ax.plot(*line),
        "scatter": lambda: ax.scatter(*points, s=20, c="tab:blue"),
    }


def measure(draw, repeats):
    samples = []
    for index in range(repeats + 3):
        start = perf_counter()
        handles = draw()
        elapsed = (perf_counter() - start) * 1000
        for handle in handles if isinstance(handles, list) else [handles]:
            handle.remove()
        if index >= 3:
            samples.append(elapsed)
    return {"median_ms": median(samples), "samples_ms": samples}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--repeats", type=int, default=25)
    cli.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parents[1] / "data")
    args = cli.parse_args()
    if args.repeats < 1:
        cli.error("--repeats must be positive")
    fig, ax = plt.subplots(subplot_kw={"projection": "vtk3d"})
    ax.set_autoscale_on(False)
    try:
        results = {name: measure(draw, args.repeats) for name, draw in workloads(ax, args.data_dir).items()}
    finally:
        ax.remove()
        plt.close(fig)
    print(json.dumps({
        "platform": platform.platform(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "matplotlib": matplotlib.__version__,
        "vtk": vtk.vtkVersion.GetVTKVersion(),
        "results": results,
    }, indent=2))


if __name__ == "__main__":
    main()
