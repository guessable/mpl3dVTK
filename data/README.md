# Example data

The examples read these NumPy archives with `np.load(path, allow_pickle=False)`. Walkthroughs are in [Examples and figure export](../docs/examples.md).

## Triangle meshes

| File | Mesh |
| --- | --- |
| [`cheese.npz`](cheese.npz) | 153,846 vertices and 307,708 triangles. Used by [`plot_trisurf`](../docs/api.md#plot_trisurf). |
| [`peanut.npz`](peanut.npz) | 2,438 vertices and 4,872 triangles. Used by [`plot_mesh`](../docs/function_reference.md#plot_mesh). |

Each archive contains `vertices` with shape `(n_vertices, 3)` in XYZ order and integer `elements` with shape `(n_faces, 3)`. The indices are zero-based. When porting a MATLAB mesh with one-based indices, subtract one from its triangle indices once.

Cheese and Peanut are byte-for-byte copies from [my-mpl-style at `d3ab92f`](https://github.com/guessable/my-mpl-style/tree/d3ab92fcaef3852701dfc2cccd22c90b5c0ecb2c/data), with the [upstream MIT notice](LICENSE-my-mpl-style.txt). See the [mesh coloring guide](../docs/function_reference.md#mesh-color-interpolation) for vertex and face colors.
