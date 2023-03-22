"""CLI interface for stubdocs."""
import argparse


class CLIArgs(argparse.Namespace):
    """Type hints for the CLI arguments."""

    stub_dir: str


def cli() -> None:
    """CLI interface."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--stub-dir", metavar="path/to/project", required=True)
    parser.add_argument("package_dir")

    args = parser.parse_args(namespace=CLIArgs())

    print(args)
