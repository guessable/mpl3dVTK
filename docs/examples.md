# 示例与验证

安装 Python 包后，在项目根目录运行以下命令。示例使用 Matplotlib Agg 和 VTK 离屏窗口。

```sh
python examples/exp_surface.py exp_surface.png
python examples/gallery.py vtk_gallery.png
python examples/chart_catalog.py chart_catalog.png
python examples/random_isosurface.py random_isosurface.png
python examples/closed_surface.py closed_surface.png --antialiasing 4
python examples/base_matlab_catalog.py --render
```

| 示例 | 图形 |
| --- | --- |
| [exp_surface.py](../examples/exp_surface.py) | 指数曲面与两个二维剖面，共用一个 Matplotlib Figure。 |
| [gallery.py](../examples/gallery.py) | 指数曲面、透明等值面与切片、三维曲线、旋转流管。 |
| [chart_catalog.py](../examples/chart_catalog.py) | 十二种基础画法的快速预览。 |
| [random_isosurface.py](../examples/random_isosurface.py) | 在 `[-1,1]^3` 的 19×19×19 网格上采独立均匀标量，提取零等值面。 |
| [closed_surface.py](../examples/closed_surface.py) | 用 `trisurf` 在封闭环面上显示标量函数，可调整抗锯齿倍数。 |
| [function_reference.py](../examples/function_reference.py) | 重新生成 [带图函数参考](function_reference.md) 中的全部图片和代码。 |
| [base_matlab_catalog.py](../examples/base_matlab_catalog.py) | 核对覆盖并生成 [基础 MATLAB 完整图集](base_matlab_3d.md) 的五张分类图。 |

随机示例可用如下写法复现标量场和等值面几何。绘图示例另外按顶点高度上色。

```python
import numpy as np
import mpl3d_vtk as m

t = np.linspace(-1, 1, 19)
V = np.random.default_rng(42).uniform(-1, 1, (19, 19, 19))
data = m.isosurface_geometry(t, t, t, V, 0)
assert data["faces"].shape[1] == 3
```

## 批量导出

`fig.savefig("figure.png", dpi=200)` 可导出 PNG。PDF 和 SVG 中，VTK 视口按指定 DPI 嵌入图像，Matplotlib 坐标框架、文本和二维曲线使用相应后端的矢量输出。Linux 无显示环境需安装提供 EGL 或 OSMesa 的 VTK 运行环境。图形资源用 `m.close(fig)` 释放。

## 本地回归和性能

```sh
python -m pip install ".[test]"
python -m pytest -q
python benchmarks/benchmark.py --surface 128 256 512 --volume 40 80 128 --frames 15
```

测试覆盖坐标轴像素一致性、正交和透视下的深度遮挡、透明视口合成、几何采样、动画更新及文件导出。性能脚本输出绘制环境、首次显示、旋转、更新高度、更新颜色的中位数和第 95 百分位耗时。等值面计时使用预先准备的体数据，测量 VTK 提取阶段。
