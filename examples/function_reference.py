"""Build the illustrated reference from the same executable examples as its code blocks."""
from dataclasses import dataclass
from pathlib import Path
import re
from types import SimpleNamespace

import matplotlib
if __name__ == "__main__":
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.tri import Triangulation
import numpy as np

import mpl3d_vtk as m


def samples():
    """Shared deterministic input arrays used by the illustrated reference."""
    t = np.linspace(-3,3,37)
    X,Y = np.meshgrid(t,t)
    s = np.linspace(-1.5,1.5,41)
    A,B,C = np.meshgrid(s,s,s)
    v = A*A + 1.5*B*B + .7*C*C
    u,w,k = -B,A,.38*np.ones_like(C)
    path = m.stream3(s,s,s,u,w,k,[.72],[0],[-1.4])
    a = np.linspace(0,2*np.pi,23,endpoint=False)
    px,py = np.r_[0,np.cos(a),.5*np.cos(a)],np.r_[0,np.sin(a),.5*np.sin(a)]
    pz = np.exp(-2*(px**2+py**2))
    tri = Triangulation(px,py).triangles
    cloud = np.random.default_rng(4).normal(size=(350,3))
    return SimpleNamespace(t=t,X=X,Y=Y,Z=m.peaks(X,Y),s=s,A=A,B=B,C=C,V=v,U=u,W=w,K=k,
                           path=path,px=px,py=py,pz=pz,tri=tri,cloud=cloud,
                           a=np.linspace(0,4*np.pi,401),b=np.array([[1,3,4],[3,1,2],[2,4,2]]))


@dataclass(frozen=True)
class Example:
    name: str
    syntax: str
    description: str
    code: str


GROUPS = {
    "规则曲面和等高线": (
        Example("surf","surf(Z[, C]) / surf(X, Y, Z[, C])",
                "Z 为高度矩阵，C 可为独立标量场或逐点 RGB(A)。X、Y 可传坐标向量。返回曲面句柄。",
                'm.surf(ax, d.X, d.Y, d.Z, FaceColor="interp", EdgeColor="none")'),
        Example("surface","surface(Z[, C]) / surface(X, Y, Z[, C])",
                "原始曲面图元，支持 XData、YData、ZData、CData 属性。连续调用可直接叠加。返回曲面句柄。",
                'm.surface(ax, XData=d.X, YData=d.Y, ZData=d.Z, FaceColor="interp", EdgeColor="none")\n'
                'm.surface(ax, d.X, d.Y, np.full_like(d.Z, 1.2), FaceColor="#739abd", '
                'FaceAlpha=.27, EdgeColor="none")'),
        Example("surfl","surfl(Z) / surfl(X, Y, Z[, light[, coefficients]])",
                "light 可为方位角和仰角，或三维方向。四个反射系数依次为环境光、漫反射、镜面反射和高光指数。附加字符串 light 可使用场景光源。",
                'm.surfl(ax, d.X, d.Y, d.Z, [-45, 35])'),
        Example("surfnorm","surfnorm(Z) / surfnorm(X, Y, Z, scale=1)",
                "用箭头标出规则网格上的曲面法向。返回曲面和箭头两个句柄。稀疏网格更易观察方向。",
                'm.surfnorm(ax, d.X[::6,::6], d.Y[::6,::6], d.Z[::6,::6], scale=.8, '
                'FaceAlpha=.65, EdgeColor="none")'),
        Example("mesh","mesh(Z[, C]) / mesh(X, Y, Z[, C])",
                "绘制随标量变化的网格线。EdgeColor 可指定固定颜色。返回网格句柄。",
                'm.mesh(ax, d.X[::3,::3], d.Y[::3,::3], d.Z[::3,::3], LineWidth=1.5)'),
        Example("surfc","surfc(X, Y, Z[, C], levels=10)",
                "在曲面下方画出高度等值线。levels 可为数量或具体高度数组。返回曲面和等高线。",
                'm.surfc(ax, d.X, d.Y, d.Z, levels=[-5,-3,-1,1,3,5], FaceColor="interp", EdgeColor="none")'),
        Example("meshc","meshc(X, Y, Z[, C], levels=10)",
                "在网格下方画出等高线。返回网格和等高线。",
                'm.meshc(ax, d.X[::2,::2], d.Y[::2,::2], d.Z[::2,::2], levels=9)'),
        Example("meshz","meshz(X, Y, Z[, C], base=None)",
                "把边界垂直延伸到 base。默认底部略低于数据最小值。返回网格和边界帘幕。",
                'm.meshz(ax, d.X[::3,::3], d.Y[::3,::3], d.Z[::3,::3], base=-7)'),
        Example("waterfall","waterfall(Z[, C]) / waterfall(X, Y, Z[, C], base=None)",
                "逐行绘制曲线和向下延伸的帘幕。返回帘幕和曲线。",
                'm.waterfall(ax, d.X[::4], d.Y[::4], d.Z[::4], LineWidth=2)'),
        Example("ribbon","ribbon(Z) / ribbon(Y, Z[, width])",
                "Z 的每列是一条带，Y 给出纵向参数。width 默认 0.75。返回带状曲面列表。",
                'R = np.sin(d.t[:,None]*[.9, 1.3, 1.7, 2.1]) + [0,.4,.8,1.2]\n'
                'm.ribbon(ax, d.t, R, .65, FaceColor="interp", EdgeColor="none")'),
        Example("contour3","contour3(Z[, levels][, LineSpec]) / contour3(X, Y, Z, ...)",
                "每条等高线位于对应的高度。标量 levels 指级别数量，数组给出具体高度。用 return_matrix=True 同时取矩阵。",
                'm.contour3(ax, d.X, d.Y, d.Z, np.linspace(-5,7,12), LineWidth=2)'),
        Example("clabel","clabel(handle, levels=None) / clabel(matrix, handle, ...)",
                "在等高线连通段上添加值标签。levels 可只标特定高度。返回 Matplotlib 3D 文字列表。",
                'h = m.contour3(ax, d.X, d.Y, d.Z, [-4, -2, 2, 4, 6], LineWidth=2)\n'
                'm.clabel(h, levels=[-4, 4, 6], fontsize=9, color="#263749")'),
        Example("fsurf","fsurf(f[, bounds]) / fsurf(fx, fy, fz[, bounds])",
                "函数接收 NumPy 数组。bounds 可设一组共用区间或分别设两个区间。MeshDensity 控制规则采样。",
                'm.fsurf(ax, lambda x,y: np.cos(x*y)*np.exp(-.2*(x*x+y*y)), [-3,3], '
                'MeshDensity=61, FaceColor="interp", EdgeColor="none")'),
        Example("fmesh","fmesh(f[, bounds]) / fmesh(fx, fy, fz[, bounds])",
                "对显式或参数曲面做规则采样，然后绘制网格。ShowContour 可附加等高线。",
                'm.fmesh(ax, lambda u,v: np.cos(u), lambda u,v: np.sin(u), lambda u,v: v, '
                '[0,2*np.pi,-1,1], MeshDensity=22)'),
        Example("fimplicit3","fimplicit3(f[, bounds], samples=51)",
                "f 接收 X、Y、Z 数组，绘制 f=0。bounds 可为两端值或三个轴各自的一对端值。",
                'm.fimplicit3(ax, lambda x,y,z: (x*x+y*y+z*z+.55**2-.18**2)**2 - 4*.55**2*(x*x+y*y), [-1,1])'),
        Example("pcolor","pcolor(C) / pcolor(X, Y, C)",
                "把矩阵映射到 XY 平面上的有色网格。颜色与网格顶点对应，默认展示顶视图。",
                'm.pcolor(ax, d.X, d.Y, d.Z, FaceColor="interp", EdgeColor="none")'),
    ),
    "三角网格、多边形和几何": (
        Example("trisurf","trisurf(TRI, X, Y, Z[, C], index_base=0)",
                "TRI 有三列，每行是一个三角形的顶点索引。也可传带 ConnectivityList、Points 或 simplices、points 的三维剖分对象。C 可为逐顶点或逐三角形颜色。",
                'm.trisurf(ax, d.tri, d.px, d.py, d.pz)'),
        Example("trimesh","trimesh(TRI, X, Y, Z[, C], index_base=0)",
                "接收相同的三角网格或剖分对象并绘制网格边。省略 Z 时，网格位于 XY 平面。",
                'm.trimesh(ax, d.tri, d.px, d.py, d.pz, LineWidth=1.5)'),
        Example("tetramesh","tetramesh(T, XYZ[, C], index_base=0)",
                "T 的每行包含四个顶点索引。XYZ 每行是三维位置。也可传入带四面体连接关系的剖分对象。C 为逐四面体标量，透明面可查看内部结构。",
                'xyz = np.array([[0,0,0],[1,0,0],[.4,1,0],[.4,.3,1],[.45,.3,-1]])\n'
                'm.tetramesh(ax, [[0,1,2,3],[0,1,2,4]], xyz, [0.,1.], FaceAlpha=.55)'),
        Example("patch","patch(Faces=faces, Vertices=xyz, FaceVertexCData=C)",
                "面可以不等长，允许用 NaN 填充。颜色可按面、按顶点或使用固定 FaceColor。",
                'xyz = np.array([[0,0,0],[1,0,0],[1,1,0],[0,1,0],[.5,.5,1]])\n'
                'm.patch(ax, Faces=[[0,1,2,3],[0,1,4],[1,2,4],[2,3,4],[3,0,4]], '
                'Vertices=xyz, FaceVertexCData=xyz[:,2], EdgeColor="#32516a", FaceAlpha=.82)'),
        Example("fill3","fill3(X, Y, Z[, C])",
                "每列给出一个封闭多边形。C 可为颜色名或映射到颜色的数据。返回面句柄。",
                'm.fill3(ax, [0,1,1,0], [0,0,1,1], [0,.2,.8,.3], "#1993a3", EdgeColor="#174859")'),
        Example("surf2patch","surf2patch(Z[, C]) / surf2patch(X, Y, Z, ..., triangles=False)",
                "把曲面转换成 faces、vertices、facevertexcdata 字典，用 triangles=True 得到三角面。",
                'g = m.surf2patch(d.X[::3,::3], d.Y[::3,::3], d.Z[::3,::3], triangles=True)\n'
                'm.patch(ax, g, EdgeColor="#334653", FaceAlpha=.9)'),
        Example("reducepatch","reducepatch(handle_or_geometry[, reduction])",
                "reduction 在 0 到 1 之间时是保留比例，也可给保留面数。返回简化几何字典。",
                'g = m.surf2patch(d.X, d.Y, d.Z, triangles=True)\n'
                'm.patch(ax, m.reducepatch(g, .06), FaceColor="#74a1bf", EdgeColor="#29485f")'),
        Example("shrinkfaces","shrinkfaces(handle_or_geometry[, factor])",
                "向各自中心收缩图元并返回拆开的面。factor 默认 0.3。",
                'g = m.surf2patch(d.X[::4,::4], d.Y[::4,::4], d.Z[::4,::4], triangles=True)\n'
                'm.patch(ax, m.shrinkfaces(g, .6), FaceColor="#457da3", EdgeColor="none")'),
        Example("alphashape","alphashape(points, alpha)",
                "points 为 N×3 数组，alpha 控制三维 Alpha 复形的外形。此 Python 入口直接绘制边界。返回面句柄。",
                'p = d.cloud / 2\nm.alphashape(ax, p, .42, FaceColor="#4b99a8", EdgeColor="#437081")'),
        Example("peaks","peaks(n=49, grid=False) / peaks(X, Y)",
                "评估二维峰谷测试函数。grid=True 返回 X、Y 和 Z，便于直接传给 surf。",
                'X, Y, Z = m.peaks(49, grid=True)\nm.surf(ax, X, Y, Z, FaceColor="interp", EdgeColor="none")'),
        Example("sphere","sphere(n=20)",
                "返回三个 (n+1)×(n+1) 的单位球面坐标数组。使用 surf 或 mesh 显示。",
                'm.surf(ax, *m.sphere(36), FaceColor="#59a3ad", EdgeColor="none", FaceLighting="gouraud")'),
        Example("cylinder","cylinder(r=1, n=20)",
                "返回沿 z 轴的旋转曲面坐标。r 可为单个半径或沿高度排列的半径数组。",
                'm.surf(ax, *m.cylinder([.45,.9,.55,.8,.32], 50), FaceColor="interp", EdgeColor="none")'),
        Example("ellipsoid","ellipsoid(xc, yc, zc, xr, yr, zr, n=20)",
                "前三项为球心，接下来三项为半轴。返回网格坐标。",
                'm.surf(ax, *m.ellipsoid(0,0,0,1.2,.7,.45,40), FaceColor="#6ea4b1", '
                'EdgeColor="none", FaceLighting="gouraud")'),
    ),
    "三维曲线、散点、统计与动画": (
        Example("plot3","plot3(X, Y, Z[, LineSpec], ...)",
                "绘制三维坐标序列。可追加多组 XYZ，或传矩阵系列、带列名的表。NaN 断开线段。",
                'm.plot3(ax, np.cos(d.a), np.sin(d.a), d.a/np.pi, LineWidth=2.5)'),
        Example("line","line(X, Y[, Z]) / line(XData=..., YData=..., ZData=...)",
                "低级线图元，保留当前场景。线宽、颜色、标记属性与 plot3 共用。",
                'm.line(ax, [0,1,1,0,0], [0,0,1,1,0], [0,0,0,0,0], LineWidth=3)\n'
                'm.line(ax, XData=[0,.5,1], YData=[0,.5,1], ZData=[0,1,0], LineWidth=3)'),
        Example("fplot3","fplot3(fx, fy, fz[, interval], samples=201)",
                "对三个参数函数共用一个参数区间。返回按采样点组成的曲线。",
                'm.fplot3(ax, np.cos, lambda t: np.sin(2*t), lambda t: t/np.pi, [0,4*np.pi], LineWidth=2.4)'),
        Example("scatter3","scatter3(X, Y, Z[, S[, C]][, marker][, filled])",
                "S 为标记面积或逐点面积，C 可为颜色名、标量或 RGB(A) 数组。返回散点句柄。",
                'p = d.cloud[:150]\nm.scatter3(ax, *p.T, 45, p[:,2], "filled")'),
        Example("bubblechart3","bubblechart3(X, Y, Z, sizes[, C])",
                "sizes 映射到气泡大小，C 映射到颜色。示例取独立数值和垂直坐标分别控制大小和颜色。",
                'p = d.cloud[:55]\nm.bubblechart3(ax, *p.T, 1+np.abs(p[:,0]), p[:,2])'),
        Example("swarmchart3","swarmchart3(X, Y, Z[, S[, C]], width=.45)",
                "同一 X 分组内，在 YZ 平面邻近的点沿 X 偏移。width 控制偏移宽度。",
                'p = d.cloud[:150]\nm.swarmchart3(ax, np.repeat([1,2,3],50), p[:,1], p[:,2], 30, p[:,2])'),
        Example("stem3","stem3(Z[, LineSpec]) / stem3(X, Y, Z[, LineSpec])",
                "用竖直线段连接 BaseValue 与每个采样点。默认基线为零。带标记时返回茎和标记句柄。",
                'x,y = np.meshgrid(np.linspace(-2,2,6), np.linspace(-2,2,6))\n'
                'm.stem3(ax,x,y,np.exp(-.4*(x*x+y*y)),"b-o",LineWidth=1.8)'),
        Example("bar3","bar3(Z) / bar3(Y, Z[, width][, style])",
                "按矩阵行列放置竖柱。style 可选 detached、grouped、stacked。正负值分别向两个方向堆叠。",
                'm.bar3(ax, d.b, .68, "detached")'),
        Example("bar3h","bar3h(Z) / bar3h(Y, Z[, width][, style])",
                "把柱高度映射到水平方向。支持独立、分组、堆叠。",
                'm.bar3h(ax, d.b, .7, "grouped")'),
        Example("histogram2","histogram2(X, Y[, bins], Normalization=..., DisplayStyle=...)",
                "双变量直方图。NumBins 或 XBinEdges、YBinEdges 可控制分箱。图元 values 包含归一化结果。",
                'm.histogram2(ax, *d.cloud[:,:2].T, NumBins=(9,9), Normalization="probability")'),
        Example("pie3","pie3(values[, explode][, labels])",
                "绘制有厚度的扇区，explode 指定需要偏移的项。labels 可由第二个或第三个参数给出。",
                'm.pie3(ax,[.45,.3,.25],[0,1,0],["A","B","C"])\nax.set_axis_off()'),
        Example("comet3","comet3(Z) / comet3(X, Y, Z[, tail], interval=30)",
                "返回定时动画。tail 是高亮尾部占轨迹的比例。离屏出图使用 set_frame 选定一帧。",
                'a = m.comet3(ax,np.cos(d.a),np.sin(d.a),d.a/np.pi,.18,LineWidth=2)\na.set_frame(320)'),
        Example("animatedline","animatedline([X, Y[, Z]], MaximumNumPoints=None)",
                "addpoints 分批追加坐标，getpoints 读回数据，clearpoints 清空。MaximumNumPoints 限制保留长度。",
                'a = m.animatedline(ax, MaximumNumPoints=280, Color="#b15768", LineWidth=2.5)\n'
                'for t in np.array_split(d.a,8):\n    m.addpoints(a,np.cos(t),np.sin(t),t/np.pi)\n'
                'x,y,z = m.getpoints(a)'),
    ),
    "标量体与向量场": (
        Example("isosurface","isosurface(V[, level[, colors]]) / isosurface(X, Y, Z, V, ...)",
                "提取指定等值，可用 colors 设置独立颜色体。noshare 展开面顶点。规则均匀体采用 Flying Edges。",
                'm.isosurface(ax,d.s,d.s,d.s,d.V,1.12,colors=d.C)'),
        Example("isosurface_geometry","isosurface_geometry(V[, level[, colors]])",
                "计算面索引、顶点和可选颜色。返回字典，可直接交给 patch。",
                'g = m.isosurface_geometry(d.s,d.s,d.s,d.V,1.03)\n'
                'm.patch(ax,g,FaceColor="#1f93a2",EdgeColor="none",FaceLighting="gouraud")'),
        Example("slice","slice([X, Y, Z,] V, xs, ys, zs[, method])",
                "xs、ys、zs 指各轴的切片位置，可用空列表跳过，或传三个曲面坐标矩阵。插值可用 linear、nearest、cubic。",
                'm.slice(ax,d.s,d.s,d.s,d.V,[0],[.4],[-.5],"linear",FaceAlpha=.92)'),
        Example("contourslice","contourslice([X, Y, Z,] V, xs, ys, zs[, levels])",
                "在各切片上绘制等值线。levels 可为自动级别数量或具体数组。返回各切片的曲线。",
                'm.contourslice(ax,d.s,d.s,d.s,d.V,[],[],[-.6,0,.6],[.4,.8,1.4,2.1],LineWidth=2)'),
        Example("isocaps","isocaps([X, Y, Z,] V, level[, enclose][, whichplane])",
                "用 above 或 below 选取阈值一侧；whichplane 为 xmin 等边界名或 all。返回端盖面。",
                'm.hold("on",ax=ax)\nm.isosurface(ax,d.s,d.s,d.s,d.V,2.8,FaceAlpha=.32)\n'
                'm.isocaps(ax,d.s,d.s,d.s,d.V,2.8,"below","zmax",FaceAlpha=.85,cmap="plasma")'),
        Example("isocolors","isocolors([X, Y, Z,] C, vertices_or_handle)",
                "对顶点位置采样颜色体。也可传 R、G、B 三个体。传入图形句柄时同时更新颜色。",
                'h = m.isosurface(ax,d.s,d.s,d.s,d.V,1.1,cmap="coolwarm")\nm.isocolors(d.s,d.s,d.s,d.A,h)'),
        Example("isonormals","isonormals([X, Y, Z,] V, vertices_or_handle[, negate])",
                "用标量体的梯度估计等值面顶点法向。negate 翻转方向。传入句柄时更新渲染法向。",
                'h = m.isosurface(ax,d.s,d.s,d.s,d.V,1.1,FaceColor="#3d93af")\nm.isonormals(d.s,d.s,d.s,d.V,h)'),
        Example("flow","flow(n=25, grid=False) / flow(X, Y, Z)",
                "生成管状标量场示例。grid=True 同时给出坐标和标量体，默认尺寸为 N×2N×N。",
                'X,Y,Z,V = m.flow(26,grid=True)\nm.isosurface(ax,X,Y,Z,V,4,colors=X)'),
        Example("smooth3","smooth3(V[, method[, size[, sigma]]])",
                "对体数据做盒式或高斯平滑。size 为奇数窗口，sigma 为高斯标准差。此图显示平滑后零等值面。",
                'v = np.random.default_rng(42).uniform(-1,1,(24,24,24))\n'
                'm.isosurface(ax,m.smooth3(v,"gaussian",5,1.1),0,FaceColor="#58a4ae")'),
        Example("reducevolume","reducevolume([X, Y, Z,] V, step)",
                "按规则步长减少数据。step 可统一指定，也可给出 x、y、z 三个轴的步长。",
                'x,y,z,v = m.reducevolume(d.s,d.s,d.s,d.V,[3,3,3])\nm.slice(ax,x,y,z,v,[0],[],[.5])'),
        Example("subvolume","subvolume([X, Y, Z,] V, limits)",
                "从规则网格提取子体。limits 顺序为 xmin、xmax、ymin、ymax、zmin、zmax，NaN 表示相应方向无限制。",
                'x,y,z,v = m.subvolume(d.s,d.s,d.s,d.V,[-.5,1,-1,1,-1,1])\n'
                'm.isosurface(ax,x,y,z,v,1.1,FaceColor="#4b939a")'),
        Example("volumebounds","volumebounds([X, Y, Z,] V) / volumebounds([X, Y, Z,] U, V, W)",
                "返回坐标边界。标量体额外返回最小最大标量值，可直接传给 axis 设置边界和颜色范围。",
                'm.isosurface(ax,d.s,d.s,d.s,d.V,.65,FaceColor="#3779a4")\n'
                'm.axis(m.volumebounds(d.s,d.s,d.s,d.V),ax=ax)'),
        Example("quiver3","quiver3([X, Y,] Z, U, V, W[, scale][, LineSpec])",
                "每个箭头由位置和分量决定。scale=0 保留实际长度。ShowArrowHead、MaxHeadSize 控制箭头。",
                't = np.linspace(-1,1,7)\nx,y,z = np.meshgrid(t,t,[-.45,.45])\n'
                'm.quiver3(ax,x,y,z,-y,x,np.full_like(x,.4),.9)'),
        Example("coneplot","coneplot([X, Y, Z,] U, V, W, Cx, Cy, Cz[, scale])",
                "在给定采样位置绘制插值得到的向量。可用颜色体、nearest 或 cubic、quiver 和 nointerp 等选项。",
                'x,y,z = np.meshgrid(np.linspace(-1,1,5),np.linspace(-1,1,5),[-.6,.6])\n'
                'm.coneplot(ax,d.s,d.s,d.s,d.U,d.W,d.K,x,y,z)'),
        Example("stream2","stream2([X, Y,] U, V, sx, sy[, options])",
                "计算二维流线顶点，options 为步长和最大步数。数组列表可交给 streamline 绘图。",
                'lines = m.stream2(d.s,d.s,d.U[:,:,0],d.W[:,:,0],[.4,.7,1.],[0,0,0])\n'
                'm.streamline(ax,lines,LineWidth=2.5)\nax.view_init(elev=90,azim=-90)'),
        Example("stream3","stream3([X, Y, Z,] U, V, W, sx, sy, sz[, options])",
                "从种子积分得到三维路径数组。可用 direction 指定 forward、backward 或 both。可传给 streamline、streamtube 等。",
                'paths = m.stream3(d.s,d.s,d.s,d.U,d.W,d.K,[.45,.8],[0,0],[-1.4,-1.4])\n'
                'm.streamline(ax,paths,LineWidth=2.5)'),
        Example("streamline","streamline(paths) / streamline([X, Y, Z,] U, V, W, sx, sy, sz)",
                "绘制已有路径，或在图中从指定种子计算并画出路径。",
                'm.streamline(ax,d.path,Color="#207c99",LineWidth=3)'),
        Example("streamslice","streamslice([X, Y, Z,] U, V, W, xs, ys, zs[, density])",
                "沿选定平面上的切向场积分。density 调节种子密度，可以用 noarrows 关闭箭头。",
                'm.streamslice(ax,d.s,d.s,d.s,d.U,d.W,d.K,[],[],[-.5,.5],.65,"noarrows",LineWidth=1.7)'),
        Example("streamtube","streamtube(paths[, widths][, [scale, sides]])",
                "把轨迹扩展为管面。可直接给向量场及种子点，或给路径及逐点管宽、散度场。radius 设置固定半径。",
                'm.streamtube(ax,d.path,radius=.045,sides=18,FaceColor="#499aaf")'),
        Example("streamribbon","streamribbon(paths[, twistangle], width=None)",
                "把三维路径扩展成带。twistangle 单位为弧度。也可用向量场以及种子点，由角速度和流速计算扭转。",
                'p = d.path[0]\nm.streamribbon(ax,[p],np.linspace(0,2*np.pi,len(p)),width=.18,FaceColor="#669ab3")'),
        Example("streamparticles","streamparticles(paths, n=20, interval=30)",
                "沿已有流线均匀放置粒子，后续帧沿点索引移动。用 set_frame 导出指定帧。",
                'm.hold("on",ax=ax)\nm.streamline(ax,d.path,Color="#b2c0cc")\n'
                'a = m.streamparticles(ax,d.path,15,color="#c05063",s=40)\na.set_frame(18)'),
        Example("curl","curl([X, Y, Z,] U, V, W)",
                "返回三个旋度分量以及速度方向上的角速度。图中对旋度做稀疏采样并绘制箭头。",
                'cu,cv,cw,_ = m.curl(d.s,d.s,d.s,d.U,d.W,d.K)\n'
                'idx = np.s_[::9,::9,::12]\n'
                'm.quiver3(ax,d.A[idx],d.B[idx],d.C[idx],cu[idx],cv[idx],cw[idx],.55)'),
        Example("divergence","divergence([X, Y, Z,] U, V, W)",
                "返回向量场的散度矩阵。图中取径向变化的场并显示一个散度切片。",
                'q = m.divergence(d.s,d.s,d.s,d.A**3,d.B**3,d.C**3)\n'
                'm.slice(ax,d.s,d.s,d.s,q,[0],[],[-.4])'),
        Example("interpstreamspeed","interpstreamspeed([X, Y, Z,] U, V, W, paths[, scale])",
                "按沿轨迹积分得到的流动时间重采样。图中用标记显示新采样点。",
                'p, = m.interpstreamspeed(d.s,d.s,d.s,d.U,d.W,d.K,d.path,5)\n'
                'm.hold("on",ax=ax)\nm.streamline(ax,[p],Color="#46758d",LineWidth=2)\n'
                'm.scatter3(ax,*p.T,35,"#c45967")'),
    ),
    "三维网络图和图像平面": (
        Example("plot","plot(edges, xyz=None) / graphplot(edges, xyz=None)",
                "绘制三维网络图。edges 每行是一条边的两个节点索引，xyz 每行是节点坐标。也可给 XData、YData、ZData，或省略坐标让 VTK 求解 force3 布局。用 directed=True 显示箭头。",
                'G = {"edges": [[0,1],[1,2],[2,3],[3,4],[4,0],[1,4],[3,0]], "directed": True}\n'
                'xyz = [[0,0,0],[1,.1,.8],[.8,1,.3],[.1,1,1],[-.25,.3,.55]]\n'
                'm.plot(ax,G,xyz,NodeLabel=["A","B","C","D","E"],MarkerSize=9,LineWidth=2)'),
        Example("graphplot", "graphplot(edges, xyz=None, **properties)",
                "从零基边列表绘制三维图。可显式传入节点位置、边颜色和标签，也可由 VTK 计算布局。",
                'edges = [[0, 1], [0, 2], [1, 2], [2, 3]]\n'
                'xyz = [[0, 0, 0], [1, 0, 0], [.6, 1, .5], [.1, .8, 1]]\n'
                'm.graphplot(ax, edges, xyz, NodeLabel=["A", "B", "C", "D"])'),
        Example("image","image(C) / image(X, Y, C, z=0)",
                "将 RGB(A) 或索引色图像放在 XY 平面。X、Y 的首尾值定义首尾像素中心。z 指平面高度，AlphaData 可为逐像素矩阵。",
                'm.hold("on",ax=ax)\n'
                'C = np.zeros((12,12,3))\n'
                'C[:] = [.15,.41,.59]\n'
                'C[(np.indices((12,12)).sum(axis=0) % 2) == 0] = [.77,.87,.92]\n'
                'm.image(ax,[-3,3],[-3,3],C,z=-2)\n'
                'm.plot3(ax,[-2,1,2],[1,-1,2],[-1,2,.5],Color="#a8484f",LineWidth=3)'),
        Example("imagesc","imagesc(C[, clims]) / imagesc(X, Y, C[, clims], z=0)",
                "把标量矩阵映射到当前色图。clims 指定数值范围，z 改变平面位置。返回可供 colorbar 使用的图元。",
                'm.hold("on",ax=ax)\n'
                'm.imagesc(ax,d.t,d.t,d.Z,[-6,8],z=-8,cmap="coolwarm")\n'
                'm.surf(ax,d.X,d.Y,d.Z,FaceAlpha=.62,FaceColor="interp",EdgeColor="none",cmap="coolwarm")'),
    ),
}

GROUPS["场景、样式和导出"] = (
    Example("text","text(x, y, z, label, **text_properties)",
            "把 Matplotlib 文字锚定在三维坐标处，支持数学公式。返回 Text3D。",
            'm.plot3(ax,np.cos(d.a),np.sin(d.a),d.a/np.pi,LineWidth=2)\n'
            'm.text(1,0,4,r"$t=4\\pi$",ax=ax,fontsize=12)'),
    Example("axis","axis(mode_or_limits, ax=ax)",
            "可传 auto、tight、equal、vis3d、on、off 或六个坐标边界，八个元素时包含色标上下限。",
            'm.surf(ax,d.X,d.Y,d.Z,FaceColor="interp",EdgeColor="none")\n'
            'm.axis([-4,4,-4,4,-8,10,-6,8],ax=ax)'),
    Example("daspect","daspect((dx, dy, dz), ax=ax)",
            "按当前轴跨度设置数据单位的显示比例。示例将三个轴的单位长度设为一致。",
            'm.surf(ax,*m.ellipsoid(0,0,0,1,.65,.4,40),FaceColor="interp",EdgeColor="none")\n'
            'm.daspect((1,1,1),ax=ax)'),
    Example("pbaspect","pbaspect((px, py, pz), ax=ax)",
            "指定三维坐标框三边的显示比例。相同数据可用更低的框显示。",
            'm.surf(ax,d.X,d.Y,d.Z,FaceColor="interp",EdgeColor="none")\nm.pbaspect((1,1,.42),ax=ax)'),
    Example("view","view(az, el) / view([az, el]) / view([x, y, z]) / view(2 or 3)",
            "用方位角和仰角或视线向量设置视角，方位角从负 y 轴起算。2 为顶视图，3 为默认三维视角。",
            'm.surf(ax,d.X,d.Y,d.Z,FaceColor="interp",EdgeColor="none")\nm.view(110,47,ax=ax)'),
    Example("camproj","camproj(mode=None, ax=ax)",
            "选择 perspective 或 orthographic。省略 mode 返回当前投影类型。",
            'm.surf(ax,d.X,d.Y,d.Z,FaceColor="interp",EdgeColor="none")\nm.camproj("orthographic",ax=ax)'),
    Example("hidden","hidden(state='on', ax=ax)",
            "控制 VTK 网格背面与被几何遮挡的部分线条是否隐藏。",
            'm.mesh(ax,d.X[::3,::3],d.Y[::3,::3],d.Z[::3,::3],Color="#3c7ca1",LineWidth=1.2)\n'
            'm.hidden("off",ax=ax)'),
    Example("shading","shading(mode='interp', ax=ax)",
            "在 flat、interp、faceted 间切换。faceted 保留边线。对已经创建的图元生效。",
            'm.surf(ax,d.X[::4,::4],d.Y[::4,::4],d.Z[::4,::4])\nm.shading("faceted",ax=ax)'),
    Example("lighting","lighting(mode='gouraud', ax=ax)",
            "为已有表面选择 none、flat、gouraud 或 phong。表面法向会随规则网格更新。",
            'm.surf(ax,*m.sphere(30),FaceColor="#62a2af",EdgeColor="none")\nm.lighting("gouraud",ax=ax)'),
    Example("camlight","camlight(az=0, el=0, ax=ax)",
            "添加跟随相机的光源，支持 left、right 或 headlight。返回 VTK 光源。",
            'm.surf(ax,*m.ellipsoid(0,0,0,1,.8,.7,40),FaceColor="#61a5b3",EdgeColor="none",FaceLighting="gouraud")\n'
            'm.camlight("right",ax=ax)'),
    Example("light","light(position=(1, 0, 1), color='white', style='infinite', ax=ax)",
            "在世界坐标中放置光源。style 可为 infinite 或 local。返回 VTK 光源。",
            'm.surf(ax,*m.sphere(40),FaceColor="#86a7b8",EdgeColor="none",FaceLighting="gouraud")\n'
            'm.light((1,-1,2),color="#ffe9c2",style="local",ax=ax)'),
    Example("lightangle","lightangle(az, el, ax=ax)",
            "以方位角和仰角设置一个固定方向光，方位角从负 y 轴起算。可用 color 指定光色。",
            'm.surf(ax,d.X,d.Y,d.Z,FaceColor="interp",EdgeColor="none",FaceLighting="gouraud",cmap="Greys")\n'
            'm.lightangle(-40,55,color="#fff0d6",ax=ax)'),
    Example("material","material(style='dull', ax=ax)",
            "设置 dull、shiny、metal 材质或四个光照系数。四个值依次为环境、漫反射、镜面反射、高光指数。",
            'm.surf(ax,*m.sphere(42),FaceColor="#357f94",EdgeColor="none",FaceLighting="gouraud")\n'
            'm.material("shiny",ax=ax)'),
    Example("colormap","colormap(cmap, ax=ax)",
            "更新场景色表，可传 Matplotlib 色表名或 RGB(A) 数组。",
            'm.surf(ax,d.X,d.Y,d.Z,FaceColor="interp",EdgeColor="none")\nm.colormap("magma",ax=ax)'),
    Example("colorbar","colorbar(handle=None, ax=ax, **kwargs)",
            "创建原生 Matplotlib 色条。默认取当前场景最后一个图元。可传 ticks、label 和 shrink。",
            'h = m.surf(ax,d.X,d.Y,d.Z,FaceColor="interp",EdgeColor="none")\n'
            'm.colorbar(h,ticks=[-6,-3,0,3,6],label="Value",shrink=.7)'),
    Example("clim","clim(limits=None, ax=ax)",
            "为当前场景设定颜色映射范围。传 auto 恢复按数据映射，省略参数返回当前范围。caxis 为同义入口。",
            'h = m.surf(ax,d.X,d.Y,d.Z,FaceColor="interp",EdgeColor="none",cmap="coolwarm")\n'
            'm.clim((-3,3),ax=ax)\nm.colorbar(h,shrink=.7)'),
    Example("alim","alim(limits=None, ax=ax)",
            "在 AlphaDataMapping 为 scaled 时设置透明度映射区间。省略参数返回当前区间。",
            'm.surf(ax,d.X,d.Y,d.Z,FaceColor="#457f9b",EdgeColor="none",FaceAlpha="interp",'
            'AlphaData=d.Z,AlphaDataMapping="scaled")\nm.alim((-5,6),ax=ax)'),
    Example("hold","hold(state='on', ax=ax)",
            "控制连续高层绘图调用是否叠加。示例将半透明参考平面与等值面画在同一轴。",
            'm.hold("on",ax=ax)\nm.isosurface(ax,d.s,d.s,d.s,d.V,1.1,FaceColor="#50a1ac")\n'
            'm.slice(ax,d.s,d.s,d.s,d.V,[],[],[-.45],FaceAlpha=.6,cmap="magma")'),
    Example("set","set(handle, Name, Value, ..., **properties)",
            "修改绘图句柄的可写属性。可使用属性名与值组成的位置参数对或 Python 关键字。",
            'h = m.surf(ax,d.X,d.Y,d.Z,EdgeColor="none")\n'
            'm.set(h,"FaceColor","#607d9f",FaceLighting="gouraud",FaceAlpha=.79)'),
    Example("grid","grid(state='on', ax=ax)",
            "切换 Matplotlib 原生三维网格线。更精细的设置可以在 ax.grid 或轴对象上完成。",
            'm.surf(ax,d.X,d.Y,d.Z,FaceColor="interp",EdgeColor="none")\nm.grid("off",ax=ax)'),
    Example("title","title(label, ax=ax, **text_properties)",
            "设置子图标题。返回原生 Matplotlib Text，可以调整字体、颜色和位置。",
            'm.surf(ax,d.X,d.Y,d.Z,FaceColor="interp",EdgeColor="none")\n'
            'm.title(r"Peaks: $z=f(x,y)$",ax=ax)\nm.xlabel("$x$",ax=ax)\n'
            'm.ylabel("$y$",ax=ax)\nm.zlabel("$z$",ax=ax)'),
    Example("xlabel", "xlabel(label, ax=ax, **text_properties)",
            "设置 x 轴标签，接受数学文本和 Matplotlib 文本属性。",
            'm.plot3(ax, [0, 1, 2], [0, 1, 0], [0, .5, 1], LineWidth=2)\n'
            'm.xlabel(r"$x$ (m)", ax=ax, color="#26778a")'),
    Example("ylabel", "ylabel(label, ax=ax, **text_properties)",
            "设置 y 轴标签，接受数学文本和 Matplotlib 文本属性。",
            'm.plot3(ax, [0, 1, 2], [0, 1, 0], [0, .5, 1], LineWidth=2)\n'
            'm.ylabel(r"$y$ (m)", ax=ax, color="#26778a")'),
    Example("zlabel", "zlabel(label, ax=ax, **text_properties)",
            "设置 z 轴标签，接受数学文本和 Matplotlib 文本属性。",
            'm.plot3(ax, [0, 1, 2], [0, 1, 0], [0, .5, 1], LineWidth=2)\n'
            'm.zlabel(r"$z$ (m)", ax=ax, color="#26778a")'),
    Example("caxis", "caxis(limits=None, ax=ax)",
            "设置场景的颜色映射范围，是 clim 的别名。示例把两端颜色锁定在 −2 和 2。",
            'h = m.surf(ax, d.X, d.Y, d.Z, FaceColor="interp", EdgeColor="none", cmap="coolwarm")\n'
            'm.caxis((-2, 2), ax=ax)\nm.colorbar(h, shrink=.7)'),
)

GROUPS["图窗、动画更新和导出"] = (
    Example("figure", "figure(*args, **kwargs)",
            "创建或激活 Matplotlib Figure。num 可为编号或名称，figsize、dpi 和 layout 沿用 Matplotlib。",
            'active = m.figure(fig.number)\n'
            'active.suptitle("Figure with a VTK scene")\n'
            'm.surf(ax, d.X, d.Y, d.Z, EdgeColor="none")'),
    Example("subplot", "subplot(*args, **kwargs)",
            "按 Matplotlib 的位置参数创建 vtk3d 子图。示例在同一 Figure 中并排绘制曲面和网格。",
            'ax.remove()\nleft = m.subplot(121)\nright = m.subplot(122)\n'
            'm.surf(left, d.X, d.Y, d.Z, EdgeColor="none")\n'
            'm.mesh(right, d.X[::4, ::4], d.Y[::4, ::4], d.Z[::4, ::4], Color="#306b84")'),
    Example("gca", "gca()",
            "返回当前 vtk3d 坐标轴。当前 Figure 没有活动的 vtk3d 轴时，创建一个三维子图。",
            'current = m.gca()\n'
            'm.plot3(current, np.cos(d.a), np.sin(d.a), d.a / np.pi, LineWidth=2)'),
    Example("drawnow", "drawnow(ax=ax)",
            "立即重绘坐标轴所属 Figure，并让 Matplotlib 后端处理事件。可用于交互循环中刷新更新的数据。",
            'h = m.animatedline(ax, LineWidth=2)\n'
            'm.addpoints(h, np.cos(d.a), np.sin(d.a), d.a / np.pi)\n'
            'm.drawnow(ax=ax)'),
    Example("show", "show(*args, **kwargs)",
            "通过 Matplotlib 的交互后端显示打开的图窗。可传 block 控制阻塞。下图为窗口中的三维场景。",
            'm.surf(ax, d.X, d.Y, d.Z, EdgeColor="none")\n'
            'if plt.get_backend().lower() != "agg":\n    m.show()'),
    Example("savefig", "savefig(path_or_buffer, **kwargs)",
            "保存当前 Figure，支持 Matplotlib 的格式、dpi 和透明背景参数。示例把 PNG 写入内存，文件名也可用作目标。",
            'from io import BytesIO\n\n'
            'm.surf(ax, d.X, d.Y, d.Z, EdgeColor="none")\n'
            'image = BytesIO()\nm.savefig(image, format="png", dpi=150)'),
    Example("close", "close(fig=None)",
            "关闭图窗并释放其 VTK 窗口。可传 Figure、图窗编号或 all。示例关闭临时图窗后继续在原图窗中出图。",
            'preview = m.figure()\n'
            'm.plot3(m.subplot(111), [0, 1], [0, 1], [0, 1])\n'
            'm.close(preview)\nm.figure(fig.number)\n'
            'm.surf(ax, d.X, d.Y, d.Z, EdgeColor="none")'),
    Example("addpoints", "addpoints(handle, x, y, z=0)",
            "向 animatedline 追加一批样本，允许标量或数组。多次追加的数据会在绘制时合并。",
            'h = m.animatedline(ax, LineWidth=2)\n'
            'for t in np.array_split(d.a, 4):\n'
            '    m.addpoints(h, np.cos(t), np.sin(t), t / np.pi)'),
    Example("getpoints", "getpoints(handle)",
            "读取 animatedline 当前保留的三个坐标数组副本。示例用散点标出读回的采样位置。",
            't = d.a[::18]\n'
            'h = m.animatedline(ax, np.cos(t), np.sin(t), t / np.pi, LineWidth=2)\n'
            'x, y, z = m.getpoints(h)\nm.hold("on", ax=ax)\n'
            'm.scatter3(ax, x, y, z, 30, "#bd616c", "filled")'),
    Example("clearpoints", "clearpoints(handle)",
            "清空 animatedline 中已有和待追加的样本，保留句柄。示例清空旧轨迹后，用同一条线开始新轨迹。",
            'h = m.animatedline(ax, np.cos(d.a), np.sin(d.a), d.a, LineWidth=2)\n'
            'm.clearpoints(h)\nt = d.a[:150]\n'
            'm.addpoints(h, np.cos(t), np.sin(t), t / np.pi)'),
    Example("Graphic", "Graphic",
            "常见 VTK 图元的返回类型，兼容 Matplotlib Artist 与 ScalarMappable。通过绘图函数取得句柄后可调颜色范围、透明度和可见性。",
            'h = m.surf(ax, d.X, d.Y, d.Z, EdgeColor="none", cmap="plasma")\n'
            'assert isinstance(h, m.Graphic)\nh.set_clim(-4, 4)\n'
            'fig.colorbar(h, ax=ax, shrink=.7)'),
    Example("VtkAxes", "VtkAxes",
            "注册为 vtk3d 的 Matplotlib Axes3D 子类，自动应用三维默认外观。用 Figure 或 pyplot 的子图方法创建。",
            'assert isinstance(ax, m.VtkAxes)\n'
            'ax.plot_surface(d.X, d.Y, d.Z, cmap=plt.get_cmap())\n'
            'ax.set(xlabel="$x$", ylabel="$y$", zlabel="$z$")'),
)

GROUPS["附加的点云、位姿与体绘制接口"] = (
    Example("pcshow", "pcshow(points, colors=None, markersize=5)",
            "显示点云。可传末维为 3 的坐标数组或 PLY/VTP 路径，颜色可按点指定，默认使用高度。",
            'm.pcshow(ax, d.cloud, markersize=4)'),
    Example("pcshowpair", "pcshowpair(first, second, markersize=5)",
            "以两种固定颜色在同一坐标轴显示两个点云，返回两个绘图句柄。",
            'm.pcshowpair(ax, d.cloud, d.cloud + [1.6, 0, .35], markersize=3)'),
    Example("plotTransforms", "plotTransforms(translations, rotations=None, *, frame_size=1, show_frame_labels=False)",
            "绘制位姿的三根坐标箭头。使用齐次 4×4 矩阵，或平移量与旋转矩阵或 wxyz 四元数。",
            't = [[0, 0, 0], [1.4, .7, .45]]\n'
            'q = [[1, 0, 0, 0], [np.cos(.4), 0, 0, np.sin(.4)]]\n'
            'm.plotTransforms(ax, t, q, frame_size=.75, show_frame_labels=True)'),
    Example("volshow", "volshow(v, *, coords=None, cmap='gray', alphamap=(0, 0, .45, .9))",
            "对均匀直角网格上的有限标量进行 VTK 体绘制。可指定色图和透明度表，或切换最大、最小或平均强度投影。",
            'v = np.exp(-3 * d.V) + .62 * np.exp(-9 * ((d.A - .6)**2 + (d.B + .5)**2 + d.C**2))\n'
            'm.volshow(ax, v, coords=(d.s, d.s, d.s), cmap="magma", alphamap=(0, .01, .12, .8))'),
)


def anchor(text):
    return re.sub(r"[^\w -]", "", text).lower().replace(" ", "-")


def write_readme_index(readme):
    start = "<!-- BEGIN ILLUSTRATED API -->"
    end = "<!-- END ILLUSTRATED API -->"
    before, remaining = readme.read_text(encoding="utf-8").split(start, 1)
    _, after = remaining.split(end, 1)
    index = [start]
    for section, examples in GROUPS.items():
        index.extend([
            "", "<details>", f"<summary>{section}（{len(examples)}）</summary>", "",
            "| 接口 | 用途 | 示例 |", "| --- | --- | --- |",
        ])
        for example in examples:
            name = example.name
            description = example.description.replace("|", r"\|")
            target = f"docs/function_reference.md#{anchor(name)}"
            preview = f'<img src="docs/figures/{name}.png" width="150" alt="{name} 示例">'
            index.append(f"| [`{name}`]({target}) | {description} | {preview} |")
        index.extend(["", "</details>"])
    index.extend(["", end])
    readme.write_text(before + "\n".join(index) + after, encoding="utf-8")


def main():
    root = Path(__file__).resolve().parents[1]
    docs = root / "docs"
    images = docs / "figures"
    images.mkdir(parents=True,exist_ok=True)
    entries = [
        "# 带图函数参考",
        "每一图均由下方代码和库中的 VTK 渲染路径生成。参数总表和兼容性范围见 [API 参考](api.md)。",
        "图集直接使用 `vtk3d` 的默认视角、轴框和刻度。每段代码列出该示例需要的视角或配色设置。",
        "先运行下面的初始化。每个例子都可以使用空的三维坐标轴独立运行。",
        '```python\nimport numpy as np\nimport matplotlib.pyplot as plt\nimport mpl3d_vtk as m\n'
        'from examples.function_reference import samples\nd = samples()\n'
        'fig, ax = plt.subplots(subplot_kw={"projection": "vtk3d"})\n```',
        '每段代码执行后可调用 `fig.savefig("example.png", dpi=160)` 查看图形。',
    ]
    entries.append("\n".join(f"- [{section}](#{anchor(section)})" for section in GROUPS))
    d = samples()
    for section, examples in GROUPS.items():
        entries.append(f"## {section}")
        for example in examples:
            fig, ax = plt.subplots(figsize=(5.1, 4.3), dpi=135, subplot_kw={"projection": "vtk3d"})
            try:
                fig.subplots_adjust(left=.07, right=.92, bottom=.13, top=.84)
                fig.suptitle(example.name, fontfamily="monospace", fontsize=13)
                exec(compile(example.code, example.name, "exec"),
                     {"np": np, "plt": plt, "m": m, "fig": fig, "ax": ax, "d": d})
                image = f"{example.name}.png"
                fig.savefig(images / image)
                frames = (panel._viewport_frame for panel in fig.axes if isinstance(panel, m.VtkAxes))
                if not any(frame is not None and np.any(frame[..., 3]) for frame in frames):
                    raise RuntimeError("no VTK geometry was visible")
            except Exception as failure:
                raise RuntimeError(f"failed example {example.name}") from failure
            finally:
                m.close(fig)
            entries.extend([f"### `{example.name}`", f"`{example.syntax}`", example.description,
                            f"```python\n{example.code}\n```",
                            f"![{example.name} 示例](figures/{image})"])
    (docs / "function_reference.md").write_text("\n\n".join(entries) + "\n", encoding="utf-8")
    write_readme_index(root / "README.md")
    print(f"Rendered {sum(map(len,GROUPS.values()))} individual examples into {images}")


if __name__ == "__main__":
    main()
