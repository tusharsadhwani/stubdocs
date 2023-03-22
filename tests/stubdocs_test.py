from textwrap import dedent

from stubdocs import add_docstring


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

    expected = dedent(
        """
        def stub_fn1(foo: str) -> int:
            \"\"\"This is the docstring\"\"\"
        def stub_fn2(bar: tuple[int], baz) -> CustomType:
            "Single quote docstring! that should work too."

        def stub_fn3():
            '''Simple docstring.

            But, it's multiline.
            '''

        @overload
        def overloaded_fn(x: int):
                '''
                Different indentation.
                This will probably cause issues.
                '''
        @overload
        def overloaded_fn(x: str) -> stuff: ...
        
        @overload
        def overloaded_fn(x: float) -> stuff:  "This is also a docstring"

        def overloaded_fn(x: int | str | float) -> Optional[stuff]:
            '''
        The joined-together function.
                    '''


        class OtherClass:
            '''Another one'''
            def some_method(self, foo:x) -> None:
                'Hey this works'
            def other_method(self, foo:x) -> None:
                return 42

        class SomeClass:
            "Some class docstring."

        class OverIndentedClass:
            '''This has extra indent in methods!'''
            def my_method(self) -> None:
                '''
                Stubs probably won't have this much indent.
                Will that work?
                '''
        
        class WeirdIndentInStub:
                    def foo():
                        ''' The doc 
                    it has under indented parts
                                and also over indented ones'''
        """
    )
    output = add_docstring(source, stub)
    assert output == expected
