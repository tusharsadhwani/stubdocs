import ast
from textwrap import dedent

import pytest

import stubdocs


def test_add_docstring() -> None:
    """Tests some_function from the package."""
    source = dedent(
        """
        def stub_fn1(foo: str) -> int:
            \"\"\"This is the docstring\"\"\"

        def stub_fn2(bar: tuple[int], baz) -> CustomType:
            "Single quote docstring! that should work too."

        def stub_fn3():
            '''Simple docstring.

            But, it's multiline.
            '''
            print("hi")



        @overload
        def overloaded_fn(x: int):
                '''
                Different indentation.
                This will probably cause issues.
                '''
                return str(x)
        @overload
        def overloaded_fn(x: str) -> stuff:  # No docstring here
            return x

        @overload
        def overloaded_fn(x: float) -> stuff:  "This is also a docstring"

        def overloaded_fn(x: int | str | float) -> Optional[stuff]:
            '''
        The joined-together function.
                    '''
            return str(x)
        class SomeClass:
            "Some class docstring."



        class OtherClass:
            '''Another one'''
            def some_method(self, foo:x):
                'Hey this works'
                return 2 + 2
            def other_method(self, bar:y) -> None:
                return 42
        
        class OverIndentedClass:
                            '''This has extra indent in methods!'''
                            def my_method(self) -> None:
                                '''
                                Stubs probably won't have this much indent.
                                Will that work?
                                '''
                                return 10

        class WeirdIndentInStub:
            def foo():
                ''' The doc 
            it has under indented parts
                        and also over indented ones'''
        """
    )
    stub = dedent(
        """
        def stub_fn1(foo: str) -> int: ...
        def stub_fn2(bar: tuple[int], baz) -> CustomType:
            ...

        def stub_fn3():
            '''This already has a docstring'''
            print("It has some content too!")

        @overload
        def overloaded_fn(x: int): ...
        @overload
        def overloaded_fn(x: str) -> stuff: ...
        
        @overload
        def overloaded_fn(x: float) -> stuff: pass

        def overloaded_fn(x: int | str | float) -> Optional[stuff]: ...


        class OtherClass:
            def some_method(self, foo:x) -> None: ...
            def other_method(self, foo:x) -> None:
                return 42

        class SomeClass:
            ...

        class OverIndentedClass:
            def my_method(self) -> None: ...
        
        class WeirdIndentInStub:
                    def foo(): ...
        """
    )

    # expected = dedent(
    #     """
    #     def stub_fn1(foo: str) -> int:
    #         \"\"\"This is the docstring\"\"\"
    #     def stub_fn2(bar: tuple[int], baz) -> CustomType:
    #         "Single quote docstring! that should work too."
    #
    #     def stub_fn3():
    #         '''Simple docstring.
    #
    #         But, it's multiline.
    #         '''
    #
    #     @overload
    #     def overloaded_fn(x: int):
    #             '''
    #             Different indentation.
    #             This will probably cause issues.
    #             '''
    #     @overload
    #     def overloaded_fn(x: str) -> stuff: ...
    #
    #     @overload
    #     def overloaded_fn(x: float) -> stuff:  "This is also a docstring"
    #
    #     def overloaded_fn(x: int | str | float) -> Optional[stuff]:
    #         '''
    #     The joined-together function.
    #                 '''
    #
    #
    #     class OtherClass:
    #         '''Another one'''
    #         def some_method(self, foo:x) -> None:
    #             'Hey this works'
    #         def other_method(self, foo:x) -> None:
    #             return 42
    #
    #     class SomeClass:
    #         "Some class docstring."
    #
    #     class OverIndentedClass:
    #         '''This has extra indent in methods!'''
    #         def my_method(self) -> None:
    #             '''
    #             Stubs probably won't have this much indent.
    #             Will that work?
    #             '''
    #
    #     class WeirdIndentInStub:
    #                 def foo():
    #                     ''' The doc
    #                 it has under indented parts
    #                             and also over indented ones'''
    #     """
    # )

    expected = dedent(
        '''\
        def stub_fn1(foo: str) -> int:
            """This is the docstring"""

        def stub_fn2(bar: tuple[int], baz) -> CustomType:
            """Single quote docstring! that should work too."""

        def stub_fn3():
            """Simple docstring.

            But, it's multiline.
            """

        @overload
        def overloaded_fn(x: int):
            """
                Different indentation.
                This will probably cause issues.
                """

        @overload
        def overloaded_fn(x: str) -> stuff:
            ...

        @overload
        def overloaded_fn(x: float) -> stuff:
            """This is also a docstring"""

        def overloaded_fn(x: int | str | float) -> Optional[stuff]:
            """
        The joined-together function.
                    """

        class OtherClass:
            """Another one"""

            def some_method(self, foo: x) -> None:
                """Hey this works"""

            def other_method(self, foo: x) -> None:
                return 42

        class SomeClass:
            """Some class docstring."""

        class OverIndentedClass:
            """This has extra indent in methods!"""

            def my_method(self) -> None:
                """
                Stubs probably won't have this much indent.
                Will that work?
                """

        class WeirdIndentInStub:

            def foo():
                """ The doc
            it has under indented parts
                        and also over indented ones"""
        '''
    )

    output = stubdocs.add_docstring(source, stub)
    assert output == expected


def test_scoper() -> None:
    """Ensure that Scoper gets the scopes right"""
    code = dedent(
        """\
        def some_global():
            ...
        
        def outer():
            def inner():
                def more_inner():
                    ...
                
            def inner_sibling():
                ...
        
        def outer_sibling():
            ...
        
        class Foo:
            def method():
                def method_inner():
                    ...
                
            def sibling_method():
                ...
        """
    )
    tree = ast.parse(code)
    scoper = stubdocs.Scoper(tree)
    scope_names = {
        node.name: scoper.get_scope(node)
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    }
    assert scope_names == {
        "some_global": "$GLOBAL",
        "outer": "$GLOBAL",
        "inner": "$GLOBAL.outer",
        "more_inner": "$GLOBAL.outer.inner",
        "inner_subling": "$GLOBAL.outer",
        "outer_sibling": "$GLOBAL",
        "method": "$GLOBAL.Foo",
        "method_inner": "$GLOBAL.Foo.inner",
        "sibling_method": "$GLOBAL.Foo",
    }


def test_scope_collision() -> None:
    """Defining two functions with same signature in same scope should raise warning."""
    simple_collision = dedent(
        """\
        def foo(x: int, y: int) -> None:
            ...

        def bar(x: int, y: int) -> None:
            ...

        def bar(x: int, y: not_int) -> None:  # No collision here
            ...

        def foo(x: int, z: int) -> None:  # No collision here
            ...

        def foo(x: int, z: int) -> NotNone:  # No collision here
            ...

        def foo(x: int, y: int, something: int) -> None:  # No collision here
            ...

        def foo(x:int,y:int) ->  None:  # COLLISION HERE
            ...
        """
    )
    root = ast.parse(simple_collision)
    with pytest.raises(stubdocs.ScopeCollisionError) as exc_info:
        stubdocs.Scoper(root)
    assert exc_info.value.args[0] == "Found overlapping function 'foo' on line 1 and 7"

    harder_collision = dedent(
        """\
        def foo(x: int, y: int) -> None:
            ...

        class Bar:
            def foo(x: int, y: int) -> None:  # This is ok
                ...
        
        def this_is_a_scope():
            def foo(x: int, y: int) -> None:  # This is also ok
                ...

        def foo(x:int,y:int) ->  None:  # THIS IS NOT OK
            ...
        """
    )

    global_but_indented_collision = dedent(
        """\
        def foo(x: int, y: int) -> None:
            ...

        with suppress(ImportError):
            def foo(x:int ,y :int)->None:
                ...
        """
    )

    collision_inside_class = dedent(
        """\
        class Bar:
            def foo(x: int, y: int) -> None:
                ...
            def bar(x:int,y:int) ->  None:  # THIS IS OK
                ...
            def foo(x:int,y:int) ->  None:  # THIS IS NOT OK
                ...
        """
    )

    collision_inside_function = dedent(
        """\
        def this_is_a_scope():
            def foo(x: int, y: int) -> None:
                ...
            def bar(x:int,y:int) ->  None:  # THIS IS OK
                ...
            def foo(x:int,y:int) ->  None:  # THIS IS NOT OK
                ...
        """
    )
