# mpl3d-vtk

[English](README.md)

`mpl3d-vtk` 为 Matplotlib 添加由 VTK 渲染的 `vtk3d` 投影。可将 NumPy 数据绘制为曲面、三角网格、标量体或向量场。坐标轴、视角、色条、布局和导出沿用 Matplotlib。

## 安装

在仓库根目录运行以下命令。

```sh
python -m pip install .
```

运行需要 Python 3.11+、NumPy 1.25+、Matplotlib 3.11.x、VTK 9.4–9.x 和可用的 OpenGL 上下文。无显示环境的配置见[导出指南](docs/examples.md#export-and-cleanup)。

## 快速开始

导入 `mpl3d_vtk` 注册投影，再用 `projection="vtk3d"` 创建子图。

```python
import matplotlib.pyplot as plt
import numpy as np
import mpl3d_vtk

t = np.linspace(-2, 2, 201)
x, y = np.meshgrid(t, t)
z = np.exp(x * np.sin(y))

fig = plt.figure(figsize=(9, 4), layout="constrained")
ax = fig.add_subplot(121, projection="vtk3d")
surface = ax.plot_surface(x, y, z, cmap="viridis")
ax.set(xlabel="x", ylabel="y", zlabel="u")
fig.colorbar(surface, ax=ax, shrink=.7)

profile = fig.add_subplot(122)
profile.plot(t, np.exp(t))
profile.set(xlabel="x", ylabel="u", title=r"$y=\pi/2$")

fig.savefig("surface.png", dpi=180)
plt.show()
```

用 `ax.view_init()` 调整视角，用 `surface.set_heights()` 或 `surface.set_values()` 更新数据。同一个坐标轴上的多个 VTK 图元共用深度缓冲区。

## 文档

详细文档采用英文。

| 任务 | 文档 |
| --- | --- |
| 按数据类型找绘图方法 | [图集](docs/plot_catalog.md) |
| 运行示例并导出图形 | [示例与导出指南](docs/examples.md) |
| 查阅绘图方法、样式和句柄 | [坐标轴与图元 API](docs/api.md) |
| 提取等值面、取切片或追踪流线 | [VTK API 参考](docs/function_reference.md) |
| 对比 Matplotlib 自带三维轴 | [三角网格和等值面基准](benchmarks/results/my_mpl_style/README.md) |
| 迁移旧代码 | [迁移指南](docs/api.md#migrating-from-older-versions) |
