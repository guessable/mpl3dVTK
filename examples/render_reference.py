"""Build the gallery, sources, and figures from the API reference."""
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
import re
from runpy import run_path
from textwrap import indent

import matplotlib
matplotlib.use("Agg")

import mpl_depth_style


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SOURCES = ROOT / "examples/reference"
RANDOM_SOURCE = ROOT / "examples/random_field_isosurface.py"
RANDOM_IMAGE = f"gallery/{RANDOM_SOURCE.stem}.png"
DATA_DIR = ROOT / "data"
PAGES = ("api.md", "scene.md")
CODE_BLOCK = re.compile(r"^\x60\x60\x60python\n(.*?)^\x60\x60\x60$", re.MULTILINE | re.DOTALL)
FIGURE = re.compile(
    rf'<img src="(gallery/reference/[^"]+\.png|{re.escape(RANDOM_IMAGE)})" width="\d+" alt="([^"]+)">'
)
HEADINGS = re.compile(r"^##(#?) (.+)\n", re.MULTILINE)
SOURCE_LINK = re.compile(r"\n\n\[Source code\]\(\.\./examples/[^)\n]+\)\.")
PLOTTING_METHODS = {"plot_surface", "plot_trisurf", "plot_isosurface", "plot", "scatter"}
STYLE_HELPERS = {"plot_rc", "ax3D_setting"}
STYLE = {
    "figure.figsize": (4.25, 3.15),
    "figure.constrained_layout.use": True,
    "figure.constrained_layout.h_pad": .15,
    "figure.constrained_layout.w_pad": .18,
    "axes.titlepad": 7,
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
    expected = {name for name in PLOTTING_METHODS if callable(getattr(mpl_depth_style.VtkAxes, name, None))}
    expected.update(name for name in STYLE_HELPERS if callable(getattr(mpl_depth_style, name, None)))
    titles = {example.title for example in examples}
    if expected != titles or len(examples) != len(titles):
        raise ValueError(
            f"Gallery entries must match the documented API. "
            f"Missing: {sorted(expected - titles)}. Unexpected: {sorted(titles - expected)}."
        )


def build_source(example, setup):
    header = f'''"""Draw {example.title}. Generated from docs/{example.page}."""
from argparse import ArgumentParser
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import mpl_depth_style'''
    style_lines = [f"    {key!r}: {value!r}," for key, value in STYLE.items()]
    style = "\n".join(["STYLE = {", *style_lines, "}"])

    dataset = example.dataset
    draw_args = "data_dir" if dataset else ""
    data_arg = ", data_dir" if dataset else ""
    body = setup + "\n\n" + example.code
    if ".ax3D_setting(" not in example.code:
        body += """

for panel in fig.axes:
    if isinstance(panel, mpl_depth_style.VtkAxes):
        mpl_depth_style.ax3D_setting(panel)"""
    draw = f"def draw({draw_args}):\n{indent(body, '    ')}\n    return fig"

    style_call = ""
    layout_call = ""
    if example.name not in ("ax3D_setting", "plot_rc"):
        style_call = '\n        mpl_depth_style.plot_rc(save_bbox="standard")'
        layout_call = "\n            fig.get_layout_engine().set(rect=(.06, .10, .88, .87))"
    save = f'''def save(output{data_arg}):
    with plt.rc_context(STYLE):{style_call}
        try:
            fig = draw({draw_args}){layout_call}
            fig.suptitle({example.title!r}, fontfamily="monospace", fontsize=12)
            fig.savefig(output, facecolor="white", dpi=140)
        finally:
            for number in plt.get_fignums():
                fig = plt.figure(number)
                for ax in fig.axes:
                    if isinstance(ax, mpl_depth_style.VtkAxes):
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
    by_name = {example.name: example for example in examples}
    groups = {}
    for example in examples:
        groups.setdefault(example.group, []).append(example)

    page = [
        "# Gallery", "",
        "Click a figure to open its API documentation. Each figure has its own runnable Python script.",
        "",
        "[Run the examples and regenerate the figures](examples.md)",
    ]
    for topic, entries in groups.items():
        columns = 3 if topic == "Plotting methods" else 2
        page.extend(["", f"## {topic}", "", "|" + " |" * columns, "|" + " :---: |" * columns])
        for offset in range(0, len(entries), columns):
            cells = []
            for entry in entries[offset:offset + columns]:
                href = f"{entry.page}#{slug(entry.title)}"
                alt = f"{entry.title}. {entry.alt}".replace("|", r"\|")
                cells.append(
                    f"[![{alt}]({entry.image})]({href})<br>"
                    f"[Documentation]({href}) · [Source code]({entry.source_href})"
                )
            cells.extend([""] * (columns - len(cells)))
            page.append("| " + " | ".join(cells) + " |")

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
