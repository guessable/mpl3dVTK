# Example data

The examples read these NumPy archives with `np.load(path, allow_pickle=False)`. Walkthroughs are in [Examples and figure export](../docs/examples.md).

## Triangle meshes

| File | Mesh |
| --- | --- |
| [`cheese.npz`](cheese.npz) | 153,846 vertices and 307,708 triangles. Used by [`plot_trisurf`](../docs/api.md#plot_trisurf). |
| [`peanut.npz`](peanut.npz) | 2,438 vertices and 4,872 triangles. Used by [`plot_mesh`](../docs/function_reference.md#plot_mesh). |
| [`armadillo.npz`](armadillo.npz) | 15,002 vertices and 30,000 triangles. Used by the spots example. |
| [`bunny.npz`](bunny.npz) | 5,002 vertices and 10,000 triangles. Used by the stripes example. |

Each archive contains `vertices` with shape `(n_vertices, 3)` in XYZ order and integer `elements` with shape `(n_faces, 3)`. The indices are zero-based. Armadillo and Bunny also retain the original scalar array `h`. When porting a MATLAB mesh with one-based indices, subtract one from its triangle indices once.

Cheese and Peanut are byte-for-byte copies from [my-mpl-style at `d3ab92f`](https://github.com/guessable/my-mpl-style/tree/d3ab92fcaef3852701dfc2cccd22c90b5c0ecb2c/data), with the [upstream MIT notice](LICENSE-my-mpl-style.txt). Armadillo and Bunny were converted from the supplied MAT files, with the triangle indices converted to zero-based indexing.

## Turing fields

The `T_end_*.npz` archives preserve the original `u_fvm` and `v_fvm` arrays. Each has shape `(1, n_vertices)`. Use `.ravel()` to get a one-dimensional array of vertex values and pair it with the corresponding mesh.

| Surface | Spots field | Stripes field |
| --- | --- | --- |
| Armadillo | [`T_end_600_spots_armadillo.npz`](T_end_600_spots_armadillo.npz) | — |
| Bunny | — | [`T_end_6000_stripes_bunny.npz`](T_end_6000_stripes_bunny.npz) |
| Egg | [`T_end_400_spots_egg.npz`](T_end_400_spots_egg.npz) | [`T_end_3600_stripes_egg.npz`](T_end_3600_stripes_egg.npz) |
| Genus-2 torus | [`T_end_400_spots_genus2torus.npz`](T_end_400_spots_genus2torus.npz) | [`T_end_3600_stripes_genus2torus.npz`](T_end_3600_stripes_genus2torus.npz) |
| Red blood cell | [`T_end_400_spots_red_blood_cell.npz`](T_end_400_spots_red_blood_cell.npz) | [`T_end_3600_stripes_red_blood_cell.npz`](T_end_3600_stripes_red_blood_cell.npz) |

The repository supplies the meshes for Armadillo and Bunny. The other fields require their corresponding meshes with the original vertex order. See the [mesh coloring guide](../docs/function_reference.md#mesh-color-interpolation) for a comparison of vertex and face colors.
