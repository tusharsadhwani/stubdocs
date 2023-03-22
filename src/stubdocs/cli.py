"""CLI interface for stubdocs."""
import argparse
from pathlib import Path

import stubdocs


class CLIArgs(argparse.Namespace):
    """Type hints for the CLI arguments."""

    stub_dir: str | None
    package_dir: str


def warning(text: str) -> None:
    """Print the string in yellow text color."""
    print(f"\033[93m{text}\033[0m")


def cli() -> None:
    """CLI interface."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--stub-dir", metavar="path/to/stubs")
    parser.add_argument("package_dir")

    args = parser.parse_args(namespace=CLIArgs())

    package_dir = Path(args.package_dir).resolve()
    if args.stub_dir is None:
        stub_dir = package_dir.parent / "out"
    else:
        stub_dir = Path(args.stub_dir).resolve()

    stub_to_source_map: dict[Path, Path] = {}
    for stub_path in stub_dir.rglob("*.pyi"):
        source_file = stub_path.name.removesuffix(".pyi") + ".py"
        source_path = Path(package_dir / source_file)
        if source_path.is_file():
            stub_to_source_map[stub_path] = source_path
        else:
            warning(f"Skipping {stub_path} as its source was not found.")

    for stub_path, source_path in stub_to_source_map.items():
        original_source = source_path.read_text()
        stub_source = source_path.read_text()
        stub_with_docstrings = stubdocs.add_docstring(original_source, stub_source)

        # TODO: rewrite the file
        print(f"rewrote stub {stub_path} using docstrings in {source_path}")
