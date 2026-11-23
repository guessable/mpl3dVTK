"""Replot and benchmark guessable/my-mpl-style data with both renderers."""
from argparse import ArgumentParser
from io import BytesIO
import json
from pathlib import Path
import platform
import subprocess
import sys
from time import perf_counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource, Normalize
import numpy as np
from skimage import __version__ as skimage_version
from skimage.measure import marching_cubes
import vtk

import mpl3d_vtk as m


MPL = "Matplotlib"
VTK = "mpl3d-vtk"
ELEVATION = 30
AZIMUTH = -127.5


def _close_figure(figure):
    for ax in figure.axes:
        if isinstance(ax, m.VtkAxes):
            ax.remove()
    plt.close(figure)


def _mesh(root, name):
    with np.load(root/"data"/f"{name}.npz", allow_pickle=False) as data:
        xyz, triangles = data["vertices"], data["elements"]
    values = None
    if name == "cheese":
        x,y,z = xyz.T
        values = x*np.sin(z) + y*np.sin(x*x)
    return name, xyz, triangles, values


def _draw_triangles(ax, renderer, data, native_aa, dpi=100):
    name, xyz, triangles, values = data
    x,y,z = xyz.T
    if values is not None:
        # Match the source example's mean per triangle, including normalization.
        face_values = values[triangles].mean(axis=1)
        norm = Normalize(float(values.min()), float(values.max()))
        if renderer == MPL:
            h = ax.plot_trisurf(x,y,z,triangles=triangles,cmap="viridis",norm=norm,
                                antialiased=native_aa,linewidth=0,shade=False)
            h.set_array(face_values)
            return h
        return ax.plot_mesh(xyz, triangles, values=face_values, association="cell", cmap="viridis", norm=norm)
    if renderer == MPL:
        return ax.plot_trisurf(x,y,z,triangles=triangles,color="#e8eef5",edgecolor="#2b5f8a",
                               linewidth=.35,antialiased=native_aa,shade=False)
    # Matplotlib expects points, whereas the VTK draw path uses output pixels.
    return ax.plot_mesh(xyz, triangles, facecolor="#e8eef5", edgecolor="#2b5f8a", linewidth=.35*dpi/72)


def _axes_parameters(data):
    name,xyz,_,_ = data
    lo,hi = xyz.min(axis=0),xyz.max(axis=0)
    if name == "cheese":
        ticks = ([-1,0,1],)*3
    else:
        lo[2],hi[2] = -.35,.35
        ticks = ([-.8,-.4,0,.4,.8],[-.3,0,.3],[-.3,0,.3])
    return list(zip(lo,hi)), ticks


def _axes(fig, loc, renderer, aa=2):
    settings = {"projection":"3d"} if renderer == MPL else {"projection":"vtk3d","antialiasing":aa}
    return fig.add_subplot(*loc, **settings)


def _format(ax, limits, ticks, source_style=None):
    if source_style is not None:
        source_style(ax,*limits,*ticks)
    else:
        ax.set(xticks=ticks[0],yticks=ticks[1],zticks=ticks[2])
        ax.set(xlim=limits[0],ylim=limits[1],zlim=limits[2])
        ax.set_aspect("equal")
        ax.set_proj_type("ortho")
        ax.view_init(elev=ELEVATION,azim=AZIMUTH)
    ax.set_xlabel("$x$",labelpad=-3)
    ax.set_ylabel("$y$",labelpad=-3)
    ax.set_zlabel("$z$",labelpad=-3)


def _native_iso(ax, coords, volume, light):
    spacing = tuple(c[1]-c[0] for c in coords)
    xyz,tri,_,_ = marching_cubes(volume,0,spacing=spacing,allow_degenerate=False)
    xyz += [c[0] for c in coords]
    ax.plot_trisurf(*xyz.T,triangles=tri,color="#18b83e",linewidth=0,
                    antialiased=False,shade=True,lightsource=light)
    return len(tri), np.column_stack((xyz.min(axis=0),xyz.max(axis=0))).tolist()


def render(root, output, meshes):
    sys.path.insert(0,str(root/"src"))
    from my_mpl_style import ax_setting3D, plot_rc

    with matplotlib.rc_context():
        plot_rc(save_dpi=215,save_bbox="standard")
        fig = plt.figure(figsize=(9.8,8.6))
        fig.subplots_adjust(left=.055,right=.93,bottom=.045,top=.895,wspace=.12,hspace=.15)
        fig.suptitle(r"Triangular meshes   $u=x\sin z+y\sin(x^2)$",fontsize=16,y=.975)
        for row,renderer in enumerate((MPL,VTK)):
            for col,data in enumerate(meshes):
                name = data[0]
                ax = _axes(fig,(2,2,row*2+col+1),renderer)
                h = _draw_triangles(ax,renderer,data,native_aa=name=="peanut",dpi=215)
                _format(ax,*_axes_parameters(data),source_style=ax_setting3D)
                title = "Matplotlib" if renderer == MPL else "VTK · 2× supersampling"
                ax.set_title(f"{name}  |  {title}",fontsize=13,pad=9)
                if name == "cheese":
                    cb = fig.colorbar(h,ax=ax,shrink=.66,fraction=.04,pad=.04)
                    cb.ax.set_title("$u$",pad=7)
        fig.savefig(output/"trisurf_comparison.png",facecolor="white")
        _close_figure(fig)

        fig = plt.figure(figsize=(12,8.1))
        fig.subplots_adjust(left=.055,right=.965,bottom=.055,top=.93,wspace=.105,hspace=.15)
        light = LightSource(azdeg=300,altdeg=38)
        iso_data = []
        for col,mean in enumerate((-.2,-.35,-.43)):
            file = root/"data"/f"pfc_3d_{col+1}_T3000.npz"
            with np.load(file,allow_pickle=False) as data:
                coords = [data[a] for a in "xyz"]
                volume = data["u_t3000"]
            ax = _axes(fig,(2,3,col+1),MPL)
            count_native,bounds_native = _native_iso(ax,coords,volume,light)
            _format(ax,[(0,50)]*3,[[0,25,50]]*3,source_style=ax_setting3D)
            ax.set_title(rf"$\bar{{\phi}}={mean:.2f}$  |  Matplotlib",fontsize=13,pad=9)
            ax = _axes(fig,(2,3,col+4),VTK)
            # Source marching cubes treats the stored volume as (x,y,z).
            # mpl3d-vtk accepts array order (y,x,z).
            h = ax.plot_isosurface(volume.transpose(1, 0, 2), coordinates=coords, level=0,
                                  facecolor="#18b83e", ambient=.33, diffuse=.67, specular=.06)
            ax.add_light(light.direction)
            _format(ax,[(0,50)]*3,[[0,25,50]]*3,source_style=ax_setting3D)
            ax.set_title(rf"$\bar{{\phi}}={mean:.2f}$  |  VTK",fontsize=13,pad=9)
            count_vtk = h.data.GetNumberOfPolys()
            bounds_vtk = np.reshape(h.data.GetBounds(),(3,2))
            np.testing.assert_allclose(bounds_vtk,bounds_native,rtol=0,atol=1e-4)
            iso_data.append({"file":file.name,"shape":volume.shape,
                             "matplotlib_triangles":count_native,"vtk_triangles":count_vtk,
                             "vtk_bounds":bounds_vtk.tolist(),"source_bounds":bounds_native})
        fig.savefig(output/"isosurface_comparison.png",facecolor="white")
        _close_figure(fig)
    return iso_data


def _timed(callback):
    start = perf_counter()
    callback()
    return (perf_counter()-start)*1000


def _summary(values):
    return {"median_ms":round(float(np.median(values)),2),
            "p95_ms":round(float(np.percentile(values,95)),2),
            "samples_ms":[round(x,3) for x in values]}


def _phase_bench(data, renderer, sampling, rotations, repeats, exports, source_style=None):
    name = data[0]
    build,first,rotate,export = [],[],[],[]
    cap = None
    for i in range(repeats):
        fig = plt.figure(figsize=(8,6),dpi=100)
        ax = _axes(fig,(1,1,1),renderer,aa=sampling)
        try:
            _format(ax,*_axes_parameters(data),source_style=source_style)
            start = perf_counter()
            handle = _draw_triangles(ax,renderer,data,bool(sampling),dpi=100)
            build.append((perf_counter()-start)*1000)
            first.append(_timed(fig.canvas.draw))
            if i+1 != repeats:
                continue
            if renderer == VTK:
                cap = [line.strip() for line in ax.window.ReportCapabilities().splitlines()
                       if "OpenGL renderer string" in line]
            for offset in np.linspace(-32,32,rotations):
                ax.view_init(elev=ELEVATION,azim=AZIMUTH+offset)
                rotate.append(_timed(fig.canvas.draw))
            if name == "peanut" and renderer == VTK:
                handle.set_linewidth(.35*200/72)
            for j in range(exports):
                ax.view_init(elev=ELEVATION,azim=AZIMUTH+2*(j+1))
                with BytesIO() as stream:
                    export.append(_timed(lambda: fig.savefig(stream,format="png",dpi=200)))
        finally:
            _close_figure(fig)
    return {"mesh":name,"vertices":len(data[1]),"triangles":len(data[2]),"renderer":renderer,
            "antialiasing":sampling,"build":_summary(build),"first_canvas_draw":_summary(first),
            "setup_to_first_image":_summary(np.add(build,first)),
            "rotate":_summary(rotate),"png_200_dpi":_summary(export),"gpu":cap}


def _git_head(root):
    return subprocess.run(["git","-C",str(root),"rev-parse","HEAD"],
                          check=True,text=True,capture_output=True).stdout.strip()


def main():
    cli = ArgumentParser(description=__doc__)
    cli.add_argument("checkout",type=Path)
    cli.add_argument("output",type=Path)
    cli.add_argument("--mode",choices=("all","render","benchmark"),default="all")
    cli.add_argument("--rotations",type=int,default=12)
    cli.add_argument("--fresh-figures",type=int,default=3)
    cli.add_argument("--exports",type=int,default=3)
    cli.add_argument("--mesh",choices=("all","cheese","peanut"),default="all")
    cli.add_argument("--renderer",choices=("all","matplotlib","vtk"),default="all")
    cli.add_argument("--vtk-aa",type=int,nargs="+",choices=(1,2,3,4),default=[1,2])
    cli.add_argument("--source-style",action="store_true",help="time with my-mpl-style axes on both sides")
    args = cli.parse_args()
    if min(args.rotations,args.fresh_figures,args.exports) < 2:
        cli.error("each timing stage needs at least two samples")
    root = args.checkout.resolve()
    dest = args.output.resolve()
    dest.mkdir(exist_ok=True,parents=True)
    head = _git_head(root)
    meshes = [_mesh(root,key) for key in ("cheese","peanut")]
    if args.mode in ("all","render"):
        geometry = render(root,dest,meshes)
        (dest/"isosurface_geometry.json").write_text(
            json.dumps({"source_commit":head,"geometry":geometry},indent=2)+"\n",encoding="utf-8")
        print("Saved both comparison figures.",flush=True)
    if args.mode in ("all","benchmark"):
        rows = []
        source_style = None
        if args.source_style:
            sys.path.insert(0,str(root/"src"))
            from my_mpl_style import ax_setting3D as source_style
        # Warm the font cache and both renderers on the small mesh first.
        for renderer,aa in ((MPL,True),(VTK,2)):
            f = plt.figure(figsize=(4,3),dpi=100)
            a = _axes(f,(1,1,1),renderer,aa)
            _draw_triangles(a,renderer,meshes[1],True)
            f.canvas.draw()
            _close_figure(f)
        for mesh in (data for data in meshes if args.mesh in ("all",data[0])):
            variants = []
            if args.renderer in ("all","matplotlib"):
                variants.extend([(MPL,False),(MPL,True)])
            if args.renderer in ("all","vtk"):
                variants.extend((VTK,aa) for aa in args.vtk_aa)
            for renderer,aa in variants if mesh[0]=="cheese" else reversed(variants):
                print(f"Timing {mesh[0]} / {renderer} / AA={aa}",flush=True)
                rows.append(_phase_bench(mesh,renderer,aa,args.rotations,args.fresh_figures,args.exports,source_style))
        stats = {"source_commit":head,"platform":platform.platform(),
                 "python":platform.python_version(),"matplotlib":matplotlib.__version__,
                 "mpl3d_vtk":m.__version__,"vtk":vtk.vtkVersion.GetVTKVersion(),
                 "numpy":np.__version__,"scikit_image":skimage_version,"backend":"Agg",
                 "canvas_px":[800,600],"png_px":[1600,1200],
                 "axes_presentation":"reference" if args.source_style else "renderer defaults",
                 "rotation_frames":args.rotations,"fresh_figures":args.fresh_figures,
                 "exports":args.exports,"results":rows}
        (dest/"trisurf_timings.json").write_text(json.dumps(stats,indent=2)+"\n",encoding="utf-8")
        print("Saved detailed timing samples.",flush=True)


if __name__ == "__main__":
    main()
