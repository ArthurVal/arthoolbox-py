#!/usr/bin/env python3

"""Functional tools for any conditional operations."""

from dataclasses import (
    dataclass,
    KW_ONLY,
)
from functools import (
    singledispatch,
)

from collections.abc import (
    Callable,
    Iterable,
    Generator,
)
from typing import (
    Any,
    Text,
    Tuple,
    Union,
    ParamSpec,
    TypeVar,
)


P = ParamSpec("P")

T = TypeVar("T")


class _NotSet:
    pass


NotSet = _NotSet()


@dataclass(frozen=True)
class ArgAt[T]:
    """Select an argument from a function argument list."""

    sel: Union[int, slice, Text]
    _: KW_ONLY
    default: T = NotSet


@singledispatch
def ForwardArg(sel, *args, **kwargs):
    """Create a functor that forward an arg by index/slice/key.

    To select the arg(s) to forward, you can either give:
    - A raw int index 'i': Forward args[i]
    - A raw str key 'key': Forward kwargs[key]
    - A slice (i.e. slice(0, 2, 3)): Forward args[slice] (a tuple)

    Each sel type can also be associated to a default value by using
    'default=V' keyword, when calling ForwardArg, in order to forward a default
    value hwne the given selector is not contained within the arg list (i.e.
    out of bound index access, etc...).

    Additionally, you can use ArgAt(sel, *, default=V) to create a single arg
    selection.

    Also, the selection can be any Iterable that will be used to forward
    multiple arguments, accodinging to the list of select arguments given.

    Examples
    --------
    - Select 1 arg by index:
    >>> fwd_arg_2 = ForwardArg(2)
    >>> fwd_arg_2("a", "b", "c", "d", foo=42)
    'c'
    >>> fwd_arg_2.__doc__
    'Forward arg[2]'

    - Select 1 arg by key:
    >>> fwd_kwarg_foo = ForwardArg("foo")
    >>> fwd_kwarg_foo(1, 2, 3, foo="Coucou")
    'Coucou'
    >>> fwd_kwarg_foo(1, 2, 3, bar="Coucou")
    KeyError: 'foo'

    - Select 1 arg with default:
    >>> fwd_kwarg_foo = ForwardArg("foo", default=32)
    >>> fwd_kwarg_foo(1, 2, 3, bar="Coucou")
    32
    >>> fwd_kwarg_foo.__doc__
    "Forward kwarg['foo'] (default to 32)"

    - Select arg with index' slice:
    >>> fwd_even_args = ForwardArg(slice(0, -1, 2))
    >>> fwd_even_args(0, "a", 2, 3, 4, 5)
    (0, 2, 4)

    - Select multiple args:
    >>> fwd_args = ForwardArg((1, "foo", 0))
    >>> list(fwd_args(0, "a", 2, 3, 4, foo=5))
    ['a', 5, 0]


    Parameters
    ----------
    sel: Union[int, slice, Text, ArgAt, Iterable]
      The index/slice/key within the input args to forward

    Returns
    -------
    Callable[P, Any]
      The functor that forward args by index, slice or key
    """
    raise TypeError(f"Unknown arg selection {sel!r} (type: {type(sel)})")


@ForwardArg.register
def _(
    arg: ArgAt,
    *,
    default: T = NotSet,
) -> Union[
    Callable[P, Any],  # int or key
    Callable[P, Union[Any, T]],  # int or key with default
    Callable[P, Tuple[Any, ...]],  # slice
    Callable[P, Union[Tuple[Any, ...], T]],  # slice with default
    Callable[P, Generator[Any]],  # Iterable
]:
    return ForwardArg(
        arg.sel,
        default=arg.default if arg.default != NotSet else default,
    )


@ForwardArg.register
def _(
    i: int,
    *,
    default: T = NotSet,
) -> Union[
    Callable[P, Any],
    Callable[P, Union[Any, T]],
]:
    if default == NotSet:

        def __impl(*args: P.args, **kwargs: P.kwargs) -> Any:
            return args[i]

        __impl.__doc__ = f"Forward arg[{i}]"

    else:

        def __impl(*args: P.args, **kwargs: P.kwargs) -> Union[Any, T]:
            return args[i] if i < len(args) else default

        __impl.__doc__ = f"Forward arg[{i}] (default to {default})"

    return __impl


@ForwardArg.register
def _(
    s: slice,
    *,
    default: T = NotSet,
) -> Union[
    Callable[P, Tuple[Any, ...]],
    Callable[P, Union[Tuple[Any, ...], T]],
]:
    if default == NotSet:

        def __impl(*args: P.args, **kwargs: P.kwargs) -> Tuple[Any, ...]:
            return args[s]

        __impl.__doc__ = f"Forward arg[{s}]"

    else:

        def __impl(
            *args: P.args, **kwargs: P.kwargs
        ) -> Union[Tuple[Any, ...], T]:
            return args[s] if s < len(args) else default

        __impl.__doc__ = f"Forward arg[{s}] (default to {default})"

    return __impl


@ForwardArg.register
def _(
    key: Text,
    *,
    default: T = NotSet,
) -> Union[
    Callable[P, Any],
    Callable[P, Union[Any, T]],
]:
    if default == NotSet:

        def __impl(*args: P.args, **kwargs: P.kwargs) -> Any:
            return kwargs[key]

        __impl.__doc__ = f"Forward kwarg[{key!r}]"

    else:

        def __impl(*args: P.args, **kwargs: P.kwargs) -> Union[Any, T]:
            return kwargs.get(key, default)

        __impl.__doc__ = f"Forward kwarg[{key!r}] (default to {default})"

    return __impl


def __brief(f: Any) -> Text:
    if f.__doc__ is None:
        return repr(f)
    else:
        return f.__doc__.partition("\n")[0].removeprefix("Forward ")


@ForwardArg.register(Iterable)
def _(
    sels: Iterable[Any],
    *,
    default: T = NotSet,
) -> Callable[P, Generator[Any]]:
    getters = [ForwardArg(a, default=default) for a in sels]

    def __impl(*args: P.args, **kwargs: P.kwargs) -> Generator[Any]:
        return (get(*args, **kwargs) for get in getters)

    __impl.__doc__ = "Forward: {args}".format(
        args=", ".join(
            (f"({i}) {__brief(get_arg)}" for i, get_arg in enumerate(getters))
        )
    )

    return __impl
