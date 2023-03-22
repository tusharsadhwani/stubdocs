# stubdocs

Adds docstrings to your type stubs.

## Installation

```bash
pip install stubdocs
```

## Usage

```console
$ stubdocs . --stub-dir stubs
rewrote stub stubs/mypackage/foo.pyi using docstrings in mypackage/foo.py
rewrote stub stubs/mypackage/bar/baz.pyi using docstrings in mypackage/bar/baz.py
```

## Local Development / Testing

- Create and activate a virtual environment
- Run `pip install -r requirements-dev.txt` to do an editable install
- Run `pytest` to run tests

## Type Checking

Run `mypy .`

## Create and upload a package to PyPI

Make sure to bump the version in `setup.cfg`.

Then run the following commands:

```bash
rm -rf build dist
python setup.py sdist bdist_wheel
```

Then upload it to PyPI using [twine](https://twine.readthedocs.io/en/latest/#installation):

```bash
twine upload dist/*
```
