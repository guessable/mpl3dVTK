"""Measure full Matplotlib draws and VTK isosurface extraction."""
import argparse
import json
import platform
from time import perf_counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import vtk

import mpl3d_vtk  # Registers the vtk3d projection.
from mpl3d_vtk._geometry import iso_filter, line_data, surface_poly, volume_grid


def timings(operation, frames):
    elapsed = []
    for i in range(frames):
        start = perf_counter()
        operation(i)
        elapsed.append(1000*(perf_counter()-start))
    return {"median_ms": round(float(np.median(elapsed)),2),
            "p95_ms": round(float(np.percentile(elapsed,95)),2)}


def surface(n, frames):
    t = np.linspace(-2,2,n)
    x,y = np.meshgrid(t,t)
    z = np.exp(x*np.sin(y))
    fig,ax = plt.subplots(figsize=(8,6),dpi=100,subplot_kw={"projection":"vtk3d"})
    ax.set(xlim=(-2,2),ylim=(-2,2),zlim=(0,8))
    ax.view_init(elev=30,azim=-60)
    try:
        start = perf_counter()
        h = ax.plot_surface(x, y, z, values=z, cmap="viridis", vmin=0., vmax=8.)
        fig.canvas.draw()
        first_draw = 1000*(perf_counter()-start)

        def rotate(i):
            ax.view_init(elev=30,azim=-60+3*i)
            fig.canvas.draw()

        heights = [z+.12*np.sin(i*.3)*np.cos(x) for i in range(frames)]

        def height(i):
            h.set_heights(heights[i])
            fig.canvas.draw()

        def color(i):
            h.set_values(heights[i])
            fig.canvas.draw()

        return {"samples":n,"quads":h.data.GetNumberOfPolys(),"first_draw_ms":round(first_draw,2),
                "geometry_build":timings(lambda _:surface_poly(x,y,z),frames),
                "rotation":timings(rotate,frames),"height_update":timings(height,frames),
                "color_update":timings(color,frames),"vtk_window":ax.window.GetClassName(),
                "renderer":ax.window.ReportCapabilities()}
    finally:
        ax.remove()
        plt.close(fig)


def segments(count, frames):
    x = np.arange(count, dtype=float)
    ends = np.column_stack((x, np.zeros_like(x), np.sin(x)))
    starts = ends.copy()
    starts[:, 2] = 0
    paths = np.stack((starts, ends), axis=1)
    return {"count": count, "geometry_build": timings(lambda _: line_data(paths), frames)}


def isosurface(n,frames):
    t = np.linspace(-2,2,n)
    x,y,z = np.meshgrid(t,t,t,sparse=True)
    values = x*x+y*y+z*z
    coords = (t,t,t)
    image = volume_grid(coords,values,image=True)
    rect = volume_grid(coords,values)
    level = 2.
    for data in (image,rect):
        iso_filter(data,[level])
    return {"samples":n,"triangles":iso_filter(image,[level]).GetNumberOfPolys(),
            "flying_edges":timings(lambda _:iso_filter(image,[level]),frames),
            "contour_filter":timings(lambda _:iso_filter(rect,[level]),frames)}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--surface",type=int,nargs="+",default=[128,256,512])
    cli.add_argument("--volume",type=int,nargs="+",default=[40,80,128])
    cli.add_argument("--segments",type=int,default=20000)
    cli.add_argument("--frames",type=int,default=15)
    args = cli.parse_args()
    if args.frames < 2 or args.segments < 2 or min(args.surface+args.volume) < 2:
        cli.error("frame count and grid sizes must be at least two")
    warmup = surface(16,2)
    caps = warmup["renderer"].splitlines()
    report = {"os":platform.platform(),"python":platform.python_version(),
              "vtk":vtk.vtkVersion.GetVTKVersion(),"matplotlib":matplotlib.__version__,
              "numpy":np.__version__,"frames":args.frames,
              "renderer":[line.strip() for line in caps if "OpenGL renderer string" in line],
              "surface":[surface(n,args.frames) for n in args.surface],
              "segments":segments(args.segments,args.frames),
              "isosurface":[isosurface(n,args.frames) for n in args.volume]}
    for row in report["surface"]:
        row.pop("renderer")
    print(json.dumps(report,indent=2))


if __name__ == "__main__":
    main()
