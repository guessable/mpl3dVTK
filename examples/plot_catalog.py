"""Render the galleries for the Matplotlib and VTK plotting APIs."""
from argparse import ArgumentParser
from pathlib import Path

from chart_catalog import main as render_charts
from function_reference import main as render_reference
from gallery import main as render_gallery


def main(destination):
    destination.mkdir(parents=True, exist_ok=True)
    render_gallery(destination / "gallery.png")
    render_charts(destination / "charts.png")
    render_reference(destination / "vtk_reference.png")


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", type=Path, default=Path("plots"))
    main(parser.parse_args().output)
