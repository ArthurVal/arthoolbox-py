#!/usr/bin/env python3

"""Set of functional tools use to ease working with callables/functors/..."""

from functools import (
    wraps,
)

from collections.abc import (
    Callable,
)
from typing import (
    Any,
    Text,
    ParamSpec,
    TypeVar,
)


P = ParamSpec("P")
R = TypeVar("R")

T = TypeVar("T")
U = TypeVar("U")


def rpartial(f, *args, **kwargs):
    """Do the same as funtools.partial (prepends instead of appending args)."""

    @wraps(f)
    def __wrapper(*fargs, **fkwargs):
        return f(*fargs, *args, **(fkwargs | kwargs))

    return __wrapper


def Brief(obj: Any) -> Text:
    """Return the brief of obj's docstring."""
    if obj.__doc__ is None:
        return repr(obj)
    else:
        return obj.__doc__.partition("\n")[0]


def DoNothing(*args, **kwargs) -> None:
    """Do Nothing."""
    pass


def Returns(v: T) -> Callable[P, T]:
    """Create a functor that ALWAYS returns v.

    Parameters
    ----------
    v: T
      Value that will ALWAYS be returned by the underlying functor created

    Returns
    -------
    Callable[P, T]
      A callable that ignore args and ALWAYS returns v.
    """

    def __impl(*args: P.args, **kwargs: P.kwargs) -> T:
        return v

    __impl.__doc__ = f"Returns {v!r}"

    return __impl


def Raises(err: T) -> Callable[P, None]:
    """Create a functor that raises err.

    Parameters
    ----------
    err: T
      Error raised

    Returns
    -------
    Callable[P, None]
      A callable that ignore args and ALWAYS raises err
    """

    def __impl(*args: P.args, **kwargs: P.kwargs) -> None:
        raise err

    __impl.__doc__ = f"Raises {err!r}"

    return __impl
