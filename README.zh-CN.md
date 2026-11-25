# mpl3d-vtk

[English](README.md)

`mpl3d-vtk` 为 Matplotlib 添加由 VTK 渲染的 `vtk3d` 投影。可将 NumPy 数据绘制为曲面、三角网格、标量体或向量场。坐标轴、视角、色条、布局和导出沿用 Matplotlib。

## 安装

```sh
python -m pip install mpl3d-vtk
```

从源码安装时，在仓库根目录运行 `python -m pip install .`。

运行需要 Python 3.11+、NumPy 1.25+、Matplotlib 3.11.x、VTK 9.4–9.x 和可用的 OpenGL 上下文。无显示环境的配置见[导出指南](docs/examples.md#export-and-cleanup)。

## 快速开始

导入 `mpl3d_vtk` 注册 `vtk3d` 投影。创建图形前调用 `mpl3d_vtk.plot_rc()`，即可给 2D 和 3D 图应用接近 MATLAB 的配色和样式。

```python
import matplotlib.pyplot as plt
import numpy as np
import mpl3d_vtk

mpl3d_vtk.plot_rc()
t = np.linspace(-2, 2, 201)
x, y = np.meshgrid(t, t)
z = np.exp(x * np.sin(y))

fig = plt.figure(figsize=(9, 4), layout="constrained")
ax = fig.add_subplot(121, projection="vtk3d")
surface = ax.plot_surface(x, y, z, cmap=plt.get_cmap())
mpl3d_vtk.ax_setting(ax)
ax.set(xlabel="x", ylabel="y", zlabel="u")
fig.colorbar(surface, ax=ax, shrink=.7)

profile = fig.add_subplot(122)
profile.plot(t, np.exp(t))
profile.set(xlabel="x", ylabel="u", title=r"$y=\pi/2$")

fig.savefig("surface.png", dpi=180)
plt.show()
```

用 `ax.view_init()` 调整视角，用 `surface.set_heights()` 或 `surface.set_values()` 更新数据。同一个坐标轴上的多个 VTK 图元共用深度缓冲区。

`ax_setting` 一次设置等比例、正交视角和刻度样式。省略范围或刻度位置时使用坐标轴的当前设置。

## 绘图示例

| 三张相交的标量切片 | 随机场的零等值面 |
| --- | --- |
| ![三张共用色条的相交标量切片](docs/gallery/intersecting_scalar_slices.png) | ![固定种子生成的绿色零等值面](docs/gallery/random_field_isosurface.png) |
| [源代码](examples/intersecting_scalar_slices.py) | [源代码](examples/random_field_isosurface.py) |

## 文档

详细文档采用英文。

- [图集](docs/plot_catalog.md) · 每张图都附有 API 文档和可运行的 Python 源代码链接。
- [示例与导出](docs/examples.md) · 运行完整脚本或保存图形。
- [示例数据](data/README.md) · 查看三角网格和 NumPy 文件格式。
- API 参考 · [绘图](docs/api.md)、[VTK 几何](docs/function_reference.md)、[场景和图元句柄](docs/scene.md)。
- [基准](benchmarks/results/my_mpl_style/README.md) · 查看与 mplot3d 的三角网格和等值面对比。
