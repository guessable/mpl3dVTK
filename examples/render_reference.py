"""Build the gallery, sources, and figures from the API reference."""
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
import re
from runpy import run_path
from textwrap import indent

import matplotlib
matplotlib.use("Agg")

import mpl3d_vtk
from mpl3d_vtk.charts import _StreamingLine
from mpl3d_vtk.planes import _ImageGraphic
from mpl3d_vtk.spatial import VolumeGraphic


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SOURCES = ROOT / "examples/reference"
RANDOM_SOURCE = ROOT / "examples/random_field_isosurface.py"
RANDOM_IMAGE = f"gallery/{RANDOM_SOURCE.stem}.png"
DATA_DIR = ROOT / "data"
PAGES = ("api.md", "function_reference.md", "scene.md")
MESH_EXAMPLES = ("plot_trisurf", "plot_mesh")
CODE_BLOCK = re.compile(r"^\x60\x60\x60python\n(.*?)^\x60\x60\x60$", re.MULTILINE | re.DOTALL)
FIGURE = re.compile(
    rf'<img src="(gallery/reference/[^"]+\.png|{re.escape(RANDOM_IMAGE)})" width="\d+" alt="([^"]+)">'
)
HEADINGS = re.compile(r"^##(#?) (.+)\n", re.MULTILINE)
SOURCE_LINK = re.compile(r"\n\n\[Source code\]\(\.\./examples/[^)\n]+\)\.")
NATIVE_METHODS = {
    mpl3d_vtk.VtkAxes: {
        "autoscale", "autoscale_view", "get_box_aspect", "get_proj",
        "get_xlim", "get_xlim3d", "get_ylim", "get_ylim3d", "get_zlim", "get_zlim3d",
    },
    VolumeGraphic: {"set_array"},
}
STYLE = {
    "figure.figsize": (4.25, 3.15),
    "figure.constrained_layout.use": True,
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.titlepad": 7,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
}


@dataclass(frozen=True)
class Example:
    page: str
    group: str
    title: str
    image: str
    alt: str
    code: str

    @property
    def name(self):
        return Path(self.image).stem

    @property
    def source(self):
        return RANDOM_SOURCE if self.image == RANDOM_IMAGE else SOURCES / f"{self.name}.py"

    @property
    def source_href(self):
        return "../" + self.source.relative_to(ROOT).as_posix()

    @property
    def dataset(self):
        match = re.search(r'data_dir / "([^"]+\.npz)"', self.code)
        return match[1] if match else None


def slug(heading):
    return re.sub(r"[^a-z0-9_ -]", "", heading.lower()).replace(" ", "-")


def read_reference():
    setups = {}
    examples = []
    for page in PAGES:
        text = (DOCS / page).read_text(encoding="utf-8")
        # Keep the shared setup body. Each generated script provides its imports.
        setups[page] = CODE_BLOCK.search(text).group(1).split("\n\n", 1)[1].strip()
        sections = list(HEADINGS.finditer(text))
        ends = [h.start() for h in sections[1:]] + [len(text)]
        for heading, end in zip(sections, ends):
            if not heading[1]:
                group = heading[2]
                continue
            section = text[heading.end():end]
            image = FIGURE.search(section)
            if image is not None:
                code = CODE_BLOCK.search(section).group(1).strip()
                examples.append(Example(page, group, heading[2].strip("\x60"), *image.groups(), code))
    if len({example.name for example in examples}) != len(examples):
        raise ValueError("Reference figure filenames must be unique.")
    return setups, examples


def check_api_coverage(examples):
    # Extraction shares the random field in plot_isosurface. Its API example returns a mesh.
    titles = {example.title for example in examples} | {"extract_isosurface"}
    missing = set(mpl3d_vtk.__all__) - titles
    classes = (mpl3d_vtk.VtkAxes, mpl3d_vtk.Graphic, VolumeGraphic, _ImageGraphic, _StreamingLine)
    for cls in classes:
        owner = cls.__name__.lstrip("_")
        for name, value in vars(cls).items():
            if (name.startswith("_") or name in NATIVE_METHODS.get(cls, ())
                    or not (callable(value) or isinstance(value, property))):
                continue
            qualified = f"{owner}.{name}"
            use_owner = name in ("set", "draw", "remove") or cls in (VolumeGraphic, _ImageGraphic)
            label = qualified if use_owner else name
            if label not in titles:
                missing.add(label)
    if missing:
        raise ValueError("Missing illustrated API entries: " + ", ".join(sorted(missing)))


def build_source(example, setup):
    header = f'''"""Draw {example.title}. Generated from docs/{example.page}."""
from argparse import ArgumentParser
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import mpl3d_vtk'''
    if "vtkplot." in example.code:
        header += "\n\nvtkplot = mpl3d_vtk"
    style_lines = [f"    {key!r}: {value!r}," for key, value in STYLE.items()]
    style = "\n".join(["STYLE = {", *style_lines, "}"])

    dataset = example.dataset
    draw_args = "data_dir" if dataset else ""
    data_arg = ", data_dir" if dataset else ""
    body = setup + "\n\n" + example.code
    # The plot_rc comparison needs to show the effects of rcParams alone.
    if example.name != "plot_rc" and ".ax_setting(" not in example.code:
        body += """

for panel in fig.axes:
    if isinstance(panel, mpl3d_vtk.VtkAxes):
        mpl3d_vtk.ax_setting(panel)"""
    draw = f"def draw({draw_args}):\n{indent(body, '    ')}\n    return fig"

    save = f'''def save(output{data_arg}):
    with plt.rc_context(STYLE):
        try:
            fig = draw({draw_args})
            fig.suptitle({example.title!r}, fontfamily="monospace", fontsize=12)
            fig.savefig(output, facecolor="white", dpi=140)
        finally:
            for number in plt.get_fignums():
                fig = plt.figure(number)
                for ax in fig.axes:
                    if isinstance(ax, mpl3d_vtk.VtkAxes):
                        ax.remove()
                plt.close(fig)'''

    cli = f'''if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", type=Path, default=Path("{example.name}.png"))'''
    if dataset:
        cli += f'''
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parents[2] / "data")
    args = parser.parse_args()
    if not (args.data_dir / "{dataset}").is_file():
        parser.error(f"Use --data-dir to locate {dataset}. File not found in {{args.data_dir}}.")
    save(args.output, args.data_dir)'''
    else:
        cli += "\n    save(parser.parse_args().output)"
    return "\n\n\n".join((header, style, draw, save, cli)) + "\n"


def write_gallery(examples):
    def figure_links(reference, source):
        return f"[Documentation]({reference}) · [Source code]({source})"

    by_name = {example.name: example for example in examples}
    random = by_name[RANDOM_SOURCE.stem]
    random_reference = f"{random.page}#{slug(random.title)}"
    groups = {"Isosurfaces and triangle meshes": [by_name[name] for name in MESH_EXAMPLES]}
    for example in examples:
        if example.name not in MESH_EXAMPLES and example is not random:
            groups.setdefault(example.group, []).append(example)

    page = [
        "# Gallery", "",
        "Each figure links to its documentation and has a runnable Python script.",
        "",
        "- **Plot data** · [Isosurfaces and triangle meshes](#isosurfaces-and-triangle-meshes) · [Surfaces](#surfaces-and-contours) · [Charts](#lines-points-and-charts) · [Scalar fields](#meshes-and-scalar-fields) · [Vector fields](#vector-fields-and-streamlines) · [Spatial geometry](#point-clouds-and-other-geometry) · [Matplotlib aliases](#matplotlib-aliases)",
        "- **Manage the scene** · [Axes](#axes-controls) · [Streaming lines and lights](#streaming-lines-and-lights) · [Matplotlib controls](#matplotlib-controls) · [Renderer integration](#renderer-integration)",
        "- **Work with a handle** · [Inspect geometry and data](#graphic-handles) · [Update data and colors](#update-data-and-colors) · [Style and visibility](#style-and-visibility) · [Specialized handles](#specialized-handles)",
    ]
    for topic, entries in groups.items():
        featured = topic == "Isosurfaces and triangle meshes"
        columns = 2 if featured else 3
        page.extend(["", f"## {topic}", ""])
        if featured:
            page.extend([
                "The triangle mesh figures use the original cheese and peanut datasets.",
                "[Example datasets](../data/README.md) · [Compare with mplot3d](../benchmarks/results/my_mpl_style/README.md)", "",
            ])
        page.extend(["|" + " |" * columns, "|" + " :---: |" * columns])
        for offset in range(0, len(entries), columns):
            cells = []
            for entry in entries[offset:offset+columns]:
                href = f"{entry.page}#{slug(entry.title)}"
                alt = f"{entry.title}. {entry.alt}".replace("|", r"\|")
                cells.append(f"[![{alt}]({entry.image})]({href})<br>{figure_links(href, entry.source_href)}")
            cells.extend([""] * (columns - len(cells)))
            page.append("| " + " | ".join(cells) + " |")
        if featured:
            page.extend([
                "", "### Random isosurface", "",
                "The zero level of a 20 × 20 × 20 field of uniform random samples in [−1, 1], with seed 42.",
                "",
                f"[![{random.title}. {random.alt}]({random.image})]({random_reference})",
                "",
                figure_links(random_reference, random.source_href),
            ])
    page.extend([
        "", "## More examples", "",
        "- [Three intersecting planes](examples.md#three-intersecting-planes)",
        "- [Run the examples or regenerate these figures](examples.md#regenerate-the-reference-figures)",
    ])
    (DOCS / "plot_catalog.md").write_text("\n".join(page) + "\n", encoding="utf-8")

    def add_link(match):
        entry = by_name[Path(match[1]).stem]
        return match[0] + f"\n\n[Source code]({entry.source_href})."

    for name in PAGES:
        path = DOCS / name
        text = SOURCE_LINK.sub("", path.read_text(encoding="utf-8"))
        path.write_text(FIGURE.sub(add_link, text), encoding="utf-8")


def main(destination, data_dir):
    setups, examples = read_reference()
    check_api_coverage(examples)
    generated = [example for example in examples if example.source.parent == SOURCES]
    datasets = {example.dataset for example in generated if example.dataset}
    missing = sorted(name for name in datasets if not (data_dir / name).is_file())
    if missing:
        raise SystemExit(f"Use --data-dir to locate the example datasets. Missing in {data_dir}: {', '.join(missing)}")
    SOURCES.mkdir(parents=True, exist_ok=True)
    destination.mkdir(parents=True, exist_ok=True)
    for example in generated:
        example.source.write_text(build_source(example, setups[example.page]), encoding="utf-8")
        save = run_path(str(example.source))["save"]
        output = destination / Path(example.image).name
        if example.dataset:
            save(output, data_dir)
        else:
            save(output)
    write_gallery(examples)
    print(f"Rendered {len(generated)} reference figures to {destination}")


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", type=Path, default=DOCS / "gallery/reference")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    args = parser.parse_args()
    main(args.output, args.data_dir)
