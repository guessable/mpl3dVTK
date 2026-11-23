"""Verify and render the complete checklist of base MATLAB 3-D examples."""
from argparse import ArgumentParser
from pathlib import Path

import matplotlib
if __name__ == "__main__":
    matplotlib.use("Agg")
import mpl3d_vtk as m
from PIL import Image, ImageDraw, ImageFont

if __package__:
    from .function_reference import GROUPS, main as render_examples
else:
    from function_reference import GROUPS, main as render_examples


DRAWING = {
    "规则曲面与等高线": (
        "surface",
        "surf surface surfl surfnorm mesh meshc meshz surfc waterfall ribbon contour3 "
        "fsurf fmesh fimplicit3 pcolor",
    ),
    "多边形和非规则网格": (
        "geometry", "patch fill3 trisurf trimesh tetramesh alphashape",
    ),
    "曲线、散点、统计和动画": (
        "charts",
        "plot3 line fplot3 scatter3 bubblechart3 swarmchart3 stem3 bar3 bar3h "
        "histogram2 pie3 comet3 animatedline",
    ),
    "体数据与流线": (
        "volume",
        "isosurface isocaps slice contourslice quiver3 coneplot streamline "
        "streamslice streamtube streamribbon streamparticles",
    ),
    "三维网络图、图像和标注": (
        "scene", "plot image imagesc text clabel",
    ),
}

DATA = {
    "网格与示例数据": "peaks sphere cylinder ellipsoid flow",
    "几何转换": "surf2patch reducepatch shrinkfaces",
    "体数据分析": "isocolors isonormals smooth3 reducevolume subvolume volumebounds",
    "流线与向量场计算": "stream2 stream3 curl divergence interpstreamspeed",
}

SOURCE_LINKS = {
    "绘图类型": "https://www.mathworks.com/help/matlab/creating_plots/types-of-matlab-plots.html",
    "曲面和网格": "https://www.mathworks.com/help/matlab/surface-and-mesh-plots-1.html",
    "多边形": "https://www.mathworks.com/help/matlab/geometry.html",
    "体可视化": "https://www.mathworks.com/help/matlab/volume-visualization.html",
    "三角剖分绘图": "https://www.mathworks.com/help/matlab/referencelist.html?category=mathematics&listtype=cat&type=function",
    "图和有向图": "https://www.mathworks.com/help/matlab/ref/graph.plot.html",
    "Alpha Shape 绘图": "https://www.mathworks.com/help/matlab/ref/alphashape.plot.html",
    "三维轴上的图像": "https://www.mathworks.com/help/matlab/ref/image.html",
}


def _contacts(figures, folder, file, names, title):
    columns = 3
    w,h = 535,385
    gutter = 18
    rows = (len(names)+columns-1)//columns
    width = columns*w + (columns+1)*gutter
    height = rows*h + (rows+1)*gutter + 60
    canvas = Image.new("RGB",(width,height),"#eef2f6")
    painter = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(str(Path(matplotlib.get_data_path())/"fonts/ttf/DejaVuSans.ttf"),30)
    painter.text((gutter,22),title,font=font,fill="#26364a")
    for i,name in enumerate(names):
        row,col = divmod(i,columns)
        with Image.open(figures/f"{name}.png") as image:
            tile = image.convert("RGB")
            tile.thumbnail((w,h),Image.Resampling.LANCZOS)
            x = gutter+col*(w+gutter)+(w-tile.width)//2
            y = 60+gutter+row*(h+gutter)+(h-tile.height)//2
            canvas.paste(tile,(x,y))
    canvas.save(folder/f"{file}.png",optimize=True)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--render",action="store_true",help="rerender all individual examples first")
    opts = parser.parse_args()
    if opts.render:
        render_examples()
    docs = Path(__file__).resolve().parents[1]/"docs"
    gallery = docs/"gallery"
    gallery.mkdir(parents=True,exist_ok=True)
    entries = {example.name for examples in GROUPS.values() for example in examples}
    charts = [name for _,spec in DRAWING.values() for name in spec.split()]
    helpers = [name for spec in DATA.values() for name in spec.split()]
    for name in charts+helpers:
        if name not in entries or not callable(getattr(m,name,None)):
            raise RuntimeError(f"missing implemented and illustrated entry: {name}")
        if not (docs/"figures"/f"{name}.png").is_file():
            raise FileNotFoundError(f"missing {name}.png; run with --render")
    if len(set(charts+helpers)) != len(charts+helpers):
        raise RuntimeError("the core checklist contains duplicate entries")

    text = [
        "# 基础 MATLAB 三维绘图清单",
        f"核对范围为基础 MATLAB R2026b 的绘图目录及三维图元用法。清单列出 **{len(charts)} 个绘图和标注入口**，"
        f"以及 **{len(helpers)} 个数据与几何辅助函数**。图中数据由 NumPy 生成，VTK 负责三维渲染，"
        "Matplotlib 负责坐标轴和排版。",
        "函数名链接到 [逐函数参考](function_reference.md) 中的签名、参数、可运行代码和独立原图。"
        "子图、照明、色标和导出见 [API 参考](api.md)。",
    ]
    titles = ("Surfaces and contours","Polygons and unstructured meshes","Curves, points and charts",
              "Volume and vector visualization","Graphs, images and annotations")
    for (section,(file,spec)),title in zip(DRAWING.items(),titles):
        names = spec.split()
        _contacts(docs/"figures",gallery,file,names,title)
        text.extend([f"## {section}（{len(names)}）",
                     " · ".join(f"[`{n}`](function_reference.md#{n})" for n in names),
                     f"![{section}全览](gallery/{file}.png)"])
    text.append("## 数据与几何辅助函数")
    for section,spec in DATA.items():
        links = " · ".join(f"[`{n}`](function_reference.md#{n})" for n in spec.split())
        text.append(f"- {section}　{links}")
    text.extend([
        "## 输入与兼容范围",
        "MATLAB 的 `plot(G)` 三维网络图对应 Python 的 `plot(edges, xyz)`，另有 `graphplot` 同义入口。"
        "MATLAB 的 `plot(alphaShape(...))` 对应 `alphashape(points, alpha)`。"
        "`sphere`、`cylinder`、`ellipsoid` 返回网格数组，可交给 `surf` 或 `mesh` 绘制。",
        "本清单的覆盖口径为基础 MATLAB 的入口及表中给出的代表性用法。"
        "完整 Handle Graphics 属性、表重载、上下文菜单、编辑器和三维查看器行为仍有实现差异。工具箱函数无需纳入基础清单。",
        "官方索引　"+" · ".join(f"[{name}]({url})" for name,url in SOURCE_LINKS.items()),
    ])
    (docs/"base_matlab_3d.md").write_text("\n\n".join(text)+"\n",encoding="utf-8")
    print(f"Verified {len(charts)} drawing and annotation entry points and {len(helpers)} data helpers.")


if __name__ == "__main__":
    main()
