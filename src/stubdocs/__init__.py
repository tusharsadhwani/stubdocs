"""stubdocs - Adds docstrings to your type stubs."""
from __future__ import annotations

import ast
from functools import lru_cache
from typing import TypeAlias


_ScopedNode: TypeAlias = ast.ClassDef | ast.FunctionDef | ast.Module


class ScopeCollisionError:
    """Raised when Scoper() finds two identical functions in the same scope."""


@lru_cache(maxsize=1)
class Scoper(ast.NodeVisitor):
    """Stores the scope of every node."""

    def __init__(self, root: ast.Module) -> None:
        self.current_scopes: tuple[_ScopedNode, ...] = (root,)
        self.scopes: dict[ast.FunctionDef, tuple[_ScopedNode, ...]] = {}
        self.scopes[root] = self.current_scopes
        self.visit(root)

    def get_scope(self, node: ast.FunctionDef) -> tuple[str, ...]:
        """Returns the scope of a given function node as a string."""
        scope_nodes = self.scopes[node]
        return ".".join(
            "$GLOBAL" if isinstance(node, ast.Module) else node.name
            for node in scope_nodes
        )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Stores the parent scope for this"""
        parent_scopes = self.current_scopes
        self.scopes[node] = parent_scopes

        # For the children, set current scope to the node itself
        self.current_scope = (*parent_scopes, node)
        super().generic_visit(node)

        # For the siblings, set scope back to parent
        self.current_scope = parent_scopes


def signature(node: ast.FunctionDef, root: ast.Module) -> tuple[str, str, str]:
    """Returns a function's signature in (scope, args, returntype) format."""
    scope_str = Scoper(root).get_scope(node)
    args_str = ast.unparse(node.args)

    if node.returns is None:
        returns_str = ""
    else:
        returns_str = ast.unparse(node.returns)

    return (scope_str, args_str, returns_str)


def add_docstring(original_source: str, stub_source: str) -> str:
    """Returns stub source code with docstrings added from original source."""
    original_ast = ast.parse(original_source)
    stub_ast = ast.parse(stub_source)

    original_functions = {
        signature(node): node
        for node in original_ast.body
        if isinstance(node, ast.FunctionDef)
    }
    stub_functions = {
        signature(node): node
        for node in stub_ast.body
        if isinstance(node, ast.FunctionDef)
    }

    for original_function_signature, original_function in original_functions.items():
        stub_function = stub_functions.get(original_function_signature)
        if stub_function is None:
            continue

        if len(original_function.body) == 0:
            continue

        docstring_node = original_function.body[0]
        if not (
            isinstance(docstring_node, ast.Expr)
            and isinstance(docstring_node.value, ast.Constant)
            and isinstance(docstring_node.value.value, str)
        ):
            # function doesn't have a docstring, don't modify stub.
            continue

        stub_function.body = [docstring_node]

    modified_stub_source = ast.unparse(stub_ast)
    print(modified_stub_source)
    return modified_stub_source
