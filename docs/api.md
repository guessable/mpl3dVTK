# API 参考

## 调用约定

导入 `mpl3d_vtk` 后可使用 `fig.add_subplot(projection="vtk3d")` 或 `m.subplot(111)`。表中的绘图函数可把坐标轴作为首个参数，或用 `ax=ax` 传入。用 `m.hold("on", ax=ax)` 叠加高层绘图调用。原始图元 `surface`、`animatedline` 和 Matplotlib 轴方法默认叠加。

```python
h = m.surf(ax, X, Y, Z, C, "FaceColor", "interp", "EdgeColor", "none")
m.set(h, FaceLighting="gouraud", FaceAlpha=.8)
fig.colorbar(h, ax=ax, label="Temperature")
```

曲面数组采用 `(ny, nx)`，体数组采用 `(ny, nx, nz)`。这对应 NumPy 的 `np.meshgrid(x, y, z, indexing="xy")`。省略规则坐标时，从 1 开始生成坐标。几何索引默认从 0 开始，`patch`、`trisurf`、`trimesh` 和 `tetramesh` 可用 `index_base=1` 读入从 1 开始的面索引。曲面中的非有限坐标挖去相邻面，曲线中的非有限坐标断开线段。

表中省略通用的轴和样式参数。普通图返回 `Graphic`，可以直接传给 Matplotlib 色条，也可以用 `vertices`、`faces`、`data`、`mapper` 和 `actor` 访问底层数据。组合图返回多个句柄。绘图函数调用时的 `Name, Value` 使用 Python 字符串与值依次传入，也可使用 Python 关键字参数。

## 曲面、图元与等高线

| 函数 | 主要输入 | 返回 |
| --- | --- | --- |
| `surf`、`surface`、`mesh` | `Z[, C]` 或 `X,Y,Z[, C]`。规则坐标可传向量。原始 `surface` 也可用 `XData,YData,ZData,CData`。 | 单个曲面句柄 |
| `surfl` | `Z` 或 `X,Y,Z`，可附加光源方向、反射系数和 `"light"`。 | 反射率着色曲面或带 VTK 光源的曲面 |
| `surfnorm` | `Z` 或 `X,Y,Z`，可用 `scale=`。 | 曲面和法向量箭头 |
| `surfc`、`meshc` | 曲面数据，`levels=` 可为数量或显式高度数组。 | 曲面和底部等高线 |
| `meshz` | 曲面数据，`base=` 设置底部高度。 | 网格和边界帘幕 |
| `waterfall` | 曲面数据，`base=` 设置底部高度。 | 帘幕和曲线 |
| `ribbon` | `Z` 或 `Y,Z[,width]`，每列一条带。 | 带状曲面列表 |
| `contour3` | `Z` 或 `X,Y,Z`，可加等高线级别和 `LineSpec`。 | 句柄。设 `return_matrix=True` 返回 `(M, handle)`。 |
| `fsurf`、`fmesh` | `f[, bounds]` 或 `fx,fy,fz[, bounds]`，`MeshDensity` 或 `samples=` 设采样密度，`ShowContour` 显示底部等高线。 | 曲面句柄或带等高线的组合 |
| `fimplicit3` | `f(x,y,z)[, bounds]`，`MeshDensity` 或 `samples=`。 | 零等值面 |
| `patch`、`fill3` | `X,Y,Z[, C]` 或 `patch(Faces=..., Vertices=..., FaceVertexCData=...)`。面可使用不同长度或 NaN 填充。 | 多边形句柄 |
| `trisurf`、`trimesh` | `TRI,X,Y,Z[, C]`。 | 三角面或网格 |
| `tetramesh` | `T, XYZ[, C]`。 | 四面体网格 |
| `pcolor` | `C` 或 `X,Y,C`。 | 位于 XY 平面的伪彩色曲面 |
| `surf2patch` | 曲面数据，可加 `"triangles"`。 | 适用于 `patch` 的字典 |
| `reducepatch`、`shrinkfaces` | 几何字典、图形句柄或 `faces,vertices`，随后可给比例。 | 包含面和顶点的字典 |

## 曲线、散点、统计与动画

| 函数 | 参数 |
| --- | --- |
| `plot3` | `X,Y,Z[,LineSpec]`，可重复数据组。支持矩阵系列以及 `table,xvar,yvar,zvar` 形式。表可以是按列名索引的字典或 DataFrame。 |
| `fplot3` | `fx,fy,fz[,interval]`，以 `samples=` 控制采样。 |
| `scatter3` | `X,Y,Z[,S[,C]][,marker][,"filled"]`。大小和颜色支持逐点数组。 |
| `bubblechart3` | `X,Y,Z,S[,C]`。大小按输入范围映射。 |
| `swarmchart3` | `X,Y,Z[,S[,C]]`，设 `width=` 控制组内偏移。 |
| `stem3` | `Z` 或 `X,Y,Z`，可加 `LineSpec`、`BaseValue`。 |
| `bar3`、`bar3h` | `Z` 或 `Y,Z`，可加宽度和 `"detached"`、`"grouped"`、`"stacked"`。 |
| `histogram2` | `X,Y[,bins]`，支持 `NumBins`、`XBinEdges`、`YBinEdges`、`Normalization`、`DisplayStyle` 和 `ShowEmptyBins`。 |
| `pie3` | `X[,explode][,labels]`。 |
| `comet3` | `Z` 或 `X,Y,Z[,tail]`。返回动画，用 `set_frame(i)` 选择离屏导出帧。 |
| `animatedline` | 可空调用或传 `X,Y[,Z]`，支持 `MaximumNumPoints`。用 `addpoints`、`getpoints`、`clearpoints` 管理数据。 |

`histogram2` 接受 `count`、`countdensity`、`probability`、`pdf`、`cumcount`、`cdf`。柱形模式的句柄带有 `values`、`x_bin_edges` 和 `y_bin_edges`。

## 体数据

| 函数 | 参数与结果 |
| --- | --- |
| `isosurface` | `V[,level[,colors]]` 或 `X,Y,Z,V[,level[,colors]]`。支持 `"noshare"` 展开面顶点和 `"verbose"` 输出网格统计。 |
| `isosurface_geometry` | 同上，返回 `faces`、`vertices`、可选 `facevertexcdata` 的字典。 |
| `slice` | `V,xs,ys,zs` 或 `X,Y,Z,V,xs,ys,zs`。三个空列表中的空项表示跳过该方向。三个矩阵可定义一张曲面。 |
| `contourslice` | 切片输入，可加末尾 `levels`。 |
| `isocaps` | 体数据、等值、可选 `"above"` 或 `"below"`，以及 `"xmin"` 等边界名。 |
| `isocolors`、`isonormals` | 输入体数据和顶点数组或句柄。前者还接受三个颜色分量体数组，后者支持 `"negate"`。 |
| `smooth3` | `V[,method[,size[,sigma]]]`，方法为 `"box"` 或 `"gaussian"`。 |
| `reducevolume`、`subvolume` | 输入体数据和步长或边界，返回 `X,Y,Z,V`。 |
| `volumebounds` | 输入标量或向量体数据，返回坐标边界及标量色标边界。 |

切片的插值方法可用末尾字符串或 `method=` 指定，支持 `"linear"`、`"nearest"`、`"cubic"`。最近邻和三次插值要求直角网格。三次插值使用局部张量积多项式。多张切片默认使用原体数据的共同色域。用 `colors` 给等值面着色时，等值决定几何位置，颜色场决定色条。

## 向量与流线

| 函数 | 参数 |
| --- | --- |
| `quiver3` | `[X,Y,]Z,U,V,W[,scale][,LineSpec][,"filled"]`，支持 `AutoScale`、`AutoScaleFactor`、`MaxHeadSize`、`ShowArrowHead`。 |
| `coneplot` | `[X,Y,Z,]U,V,W,Cx,Cy,Cz`，可加缩放或颜色、`"quiver"` 和插值方法。完整位置和分量可用 `"nointerp"`。 |
| `stream2`、`stream3` | 向量场、种子点及可选 `[step,max_steps]`，返回顶点数组列表。 |
| `streamline` | 路径列表或向量场及种子点。 |
| `streamslice` | 向量场和轴向切片位置，二维场可省略切片位置。支持 `density`、`"arrows"`、`"noarrows"`。 |
| `streamtube` | 路径、管宽或散度，也可给体向量场和种子点。可附加 `[scale,sides]`。 |
| `streamribbon` | 路径及扭转角、旋度和速度体数据，或体向量场与种子点。可指定 `width`。 |
| `streamparticles` | 路径和粒子数，返回可用 `set_frame` 定位的动画。 |
| `curl`、`divergence`、`interpstreamspeed` | 直角网格向量场分析和流线重采样。 |

流线使用 VTK 的 RK4 和线性场插值。箭头自动缩放、流线种子分布和积分结果依数据与网格而变，允许在比较图形时显式锁定种子点、步长和缩放。

## 样式、光照与坐标轴

- 曲面支持 `FaceColor="flat"|"interp"|"none"` 或固定颜色，`EdgeColor` 独立设置，`FaceAlpha` 可给常数或配合 `AlphaData` 使用 `"interp"`、`"flat"`。用 `clim`、`caxis` 和 `alim` 设置映射区间。
- `CDataMapping="direct"` 使用从 1 起的色表索引。支持 Matplotlib 色图名和 RGB(A) 色表数组。默认的 `scaled` 对标量数据使用归一化。
- `lighting`、`camlight`、`light`、`lightangle`、`material` 管理光照。曲面可调 `AmbientStrength`、`DiffuseStrength`、`SpecularStrength`、`SpecularExponent`。
- `view(az, el)` 以负 y 轴为方位角零点，正角朝正 x 轴旋转。换算为原生方法是 `ax.view_init(elev=el, azim=az-90)`。用 `camproj` 或 `ax.set_proj_type` 设置投影。
- `DisplayName` 对应原生 `ax.legend()`，`Visible`、`FaceColor`、`LineWidth` 等可通过 `m.set` 或句柄方法修改。用 `set_zdata()`、`set_cdata()` 批量更新曲面。

### 默认三维坐标轴

`projection="vtk3d"` 默认使用正交投影，仰角为 30°，原生方位角为 −127.5°。坐标轴使用等数据单位比例、灰色无填充轴框、0.2 pt 网格线和向外刻度。刻度线长度取最长投影轴的 2%，轴范围及刻度位置由当前数据和 Matplotlib 的定位器确定。

背景、色图和颜色循环取自 Matplotlib 当前样式。标量着色默认使用 `rcParams["image.cmap"]`。绘图调用中的 `cmap` 和 `Color` 可指定具体图元的配色。

### 抗锯齿

每个 `vtk3d` 坐标轴默认按宽高各 2 倍渲染 VTK 场景，再降采样到输出尺寸。曲面轮廓、细线、散点、图像平面及透明图元共用这一设置，Matplotlib 的坐标和文字使用其自身的抗锯齿。

```python
ax = fig.add_subplot(111, projection="vtk3d", antialiasing=2)
ax.set_antialiasing(4)
fig.savefig("surface.png", dpi=175)
```

`antialiasing` 接受整数 1 到 4。1 按原始分辨率出图，2 是默认，4 适合导出后需要放大查看的图。每个坐标轴可独立设置，也可用 `ax.get_antialiasing()` 查看。倍数越高，离屏缓冲区、GPU 光栅化和读取像素的开销越大。数据顶点和连接关系由原始输入决定，抗锯齿处理的是渲染后的像素边缘。

## 三维网络图和图像

| 函数 | 参数与结果 |
| --- | --- |
| `plot`、`graphplot` | `edges[, xyz]`，边为零基整数对，位置可为 N×3 数组或 XData、YData、ZData。无坐标时用 VTK 的 force3。可设 directed、ShowArrows、NodeLabel、NodeColor、MarkerSize、LineWidth。 |
| `image` | `C` 或 `X,Y,C`。支持索引色、RGB(A)，默认 z=0。X、Y 的首尾位置是首尾像素中心。 |
| `imagesc` | 图像数据及可选 `clims`，使用缩放色图。可接原生 Matplotlib 色条。 |

`image` 和 `imagesc` 使用一个四边形及 VTK 纹理。可设置 `AlphaData`、`AlphaDataMapping`、`Interpolation`，用 `set_cdata` 在原尺寸更新像素。 [图像示例](function_reference.md#image)

## 支持范围

[三维绘图图集](plot_catalog.md)列出主要绘图入口及数据辅助函数。各函数支持的签名、属性和代码见 [逐函数参考](function_reference.md)。线型及标记的屏幕尺寸受渲染后端与绘图方式影响。

## 图窗和动画辅助

| 函数 | 用法 |
| --- | --- |
| `figure(*args, **kwargs)` | 按 Matplotlib Figure 的参数创建或激活图窗。 |
| `subplot(*args, **kwargs)` | 创建三维子图，如 `m.subplot(221)`。也可用 Matplotlib 的 `fig.add_subplot(..., projection="vtk3d")`。 |
| `gca()` | 获取当前三维轴，或在当前 Figure 中创建。 |
| `show(*args, **kwargs)` | 将调用转给 `matplotlib.pyplot.show`，在交互后端显示窗口。 |
| `savefig(path, **kwargs)` | 把当前 Figure 写到文件，可用 `dpi`、`transparent` 等 Matplotlib 参数。 |
| `close(fig=None)` | 关闭图形并释放 VTK 窗口。可传 Figure 或 `"all"`。 |
| `drawnow(ax=ax)` | 立即重绘当前 Figure 并处理事件。 |
| `addpoints(handle, x, y, z=0)` | 将新样本加入 `animatedline`，在重绘时刷新几何。 |
| `getpoints(handle)` | 返回当前动画的三个坐标数组副本。 |
| `clearpoints(handle)` | 清空动画轨迹和待追加样本。 |

图窗、色条与动画的完整示例见 [带图函数参考](function_reference.md)。
