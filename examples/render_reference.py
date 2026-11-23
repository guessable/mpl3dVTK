"""Render the figures in the API reference from their Markdown examples."""
from argparse import ArgumentParser
from pathlib import Path
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoLocator, MaxNLocator

import mpl3d_vtk


ROOT = Path(__file__).resolve().parents[1]
PAGES = ("api.md", "function_reference.md", "scene.md")
CODE_BLOCK = re.compile(r"^\x60\x60\x60python\n(.*?)^\x60\x60\x60$", re.MULTILINE | re.DOTALL)
FIGURE = re.compile(r'<img src="(gallery/reference/[^"]+\.png)"')


def examples(page):
    text = page.read_text(encoding="utf-8")
    sections = re.split(r"^#{2,3} (.+)\n", text, flags=re.MULTILINE)
    setup = CODE_BLOCK.search(text).group(1)
    for heading, section in zip(sections[1::2], sections[2::2]):
        image = FIGURE.search(section)
        if image is None:
            continue
        code = CODE_BLOCK.search(section)
        if code is None:
            raise ValueError(f"No example for {image.group(1)} in {page.name}")
        yield heading.strip("`"), Path(image.group(1)).name, setup, code.group(1)


def render(path, title, setup, code):
    namespace = {}
    try:
        exec(compile(setup, str(path), "exec"), namespace)
        exec(compile(code, str(path), "exec"), namespace)
        figure = namespace["fig"]
        for ax in figure.axes:
            if isinstance(ax, mpl3d_vtk.VtkAxes):
                for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
                    if isinstance(axis.get_major_locator(), AutoLocator):
                        axis.set_major_locator(MaxNLocator(nbins=3))
        figure.suptitle(title, fontfamily="monospace", fontsize=12)
        figure.savefig(path, facecolor="white", dpi=140)
    finally:
        for number in plt.get_fignums():
            figure = plt.figure(number)
            for ax in figure.axes:
                if isinstance(ax, mpl3d_vtk.VtkAxes):
                    ax.remove()
            plt.close(figure)


def main(destination):
    destination.mkdir(parents=True, exist_ok=True)
    names = set()
    style = {
        "figure.figsize": (4.25, 3.15),
        "figure.constrained_layout.use": True,
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.titlepad": 7,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
    }
    with matplotlib.rc_context(style):
        for page in PAGES:
            for title, name, setup, code in examples(ROOT / "docs" / page):
                if name in names:
                    raise ValueError(f"Duplicate reference figure: {name}")
                render(destination / name, title, setup, code)
                names.add(name)
    print(f"Rendered {len(names)} figures to {destination}")


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", type=Path, default=ROOT / "docs/gallery/reference")
    main(parser.parse_args().output)
