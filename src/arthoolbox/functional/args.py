#!/usr/bin/env python3

"""Functional tools for any conditional operations."""

from dataclasses import (
    dataclass,
    KW_ONLY,
    MISSING,
)

from collections.abc import (
    Callable,
)
from typing import (
    Any,
    Text,
    Union,
    ParamSpec,
)


P = ParamSpec("P")


@dataclass(frozen=True)
class AtIdx:
    """TODO."""

    i: Union[int | slice]
    _: KW_ONLY
    default: Any = MISSING


@dataclass(frozen=True)
class WithKey:
    """TODO."""

    key: Text
    _: KW_ONLY
    default: Any = MISSING


def ForwardArg(arg: Union[int, AtIdx, Text, WithKey]) -> Callable[P, Any]:
    """Create a functor that forward a single arg, either by index of key.

    Parameters
    ----------
    arg: Union[int, AtIdx, Text, WithKey]
      If an interger is given, forwards args[i]. Otherwise (a key str), forward
      kwargs[key].


    Returns
    -------
    Callable[P, Any]
      The functor that filter args
    """
    if isinstance(arg, (int, slice)):
        return ForwardArg(AtIdx(arg))
    elif isinstance(arg, Text):
        return ForwardArg(WithKey(arg))
    elif isinstance(arg, AtIdx):
        if isinstance(arg.default, MISSING):

            def __impl(*args: P.args, **kwargs: P.kwargs) -> Any:
                return args[arg.i]

            __impl.__doc__ = f"Forward arg[{arg.i}]"

        else:

            def __impl(*args: P.args, **kwargs: P.kwargs) -> Any:
                return args[arg.i] if len(args) < arg.i else arg.default

            __impl.__doc__ = (
                f"Forward arg[{arg.i}] (default to: {arg.default!r})"
            )

    elif isinstance(arg, WithKey):
        if isinstance(arg.default, MISSING):

            def __impl(*args: P.args, **kwargs: P.kwargs) -> Any:
                return kwargs[arg.key]

            __impl.__doc__ = f"Forward kwarg[{arg.key!r}]"

        else:

            def __impl(*args: P.args, **kwargs: P.kwargs) -> Any:
                return kwargs.get(arg.key, default=arg.default)

            __impl.__doc__ = (
                f"Forward kwarg[{arg.key!r}] (default to: {arg.default!r})"
            )

    else:
        raise ValueError(
            f"ID should be either an int or a str (got '{type(arg)}')"
        )

    return __impl
