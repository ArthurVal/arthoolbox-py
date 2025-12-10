#!/usr/bin/env python3

"""Functional tools for any conditional operations."""

from .core import (
    Brief,
    DoNothing,
)

from collections.abc import (
    Callable,
)
from typing import (
    Any,
    Concatenate,
    Union,
    TypeVar,
    ParamSpec,
)

P = ParamSpec("P")

T = TypeVar("T")
U = TypeVar("U")


def When(
    pred: Callable[P, bool],
    do: Callable[P, T],
    otherwise: Callable[P, U] = DoNothing,
) -> Callable[P, Union[T, U]]:
    """Call either `R = do(..)` or `R = otherwise(...)` based on `pred(...)`.

    Parameters
    ----------
    pred: Callable[P, bool]
      Predicate called with input args.
    do: Callable[P, T]
      Action done with input args whenever pred returned True
    otherwise: Callable[P, U]
      Action done with input args whenever pred returned False

    Returns
    -------
    Callable[P, Union[T, U]]
      A callable that perform a branch returning `do(...)` or `otherwise(...)`
      based on `pred(...)`
    """

    def __impl(*args: P.args, **kwargs: P.kwargs) -> Union[T, U]:
        if pred(*args, **kwargs):
            return do(*args, **kwargs)
        else:
            return otherwise(*args, **kwargs)

    __impl.__doc__ = "When '{pred}', do '{do}'. Otherwise '{otherwise}'".format(
        pred=Brief(pred),
        do=Brief(do),
        otherwise=Brief(otherwise),
    )

    return __impl


def WhenFailing(
    f: Callable[P, T],
    do: Callable[Concatenate[Any, P], U],
    *,
    error_type: type = Exception,
) -> Callable[P, Union[T, U]]:
    """Decorate `R = f(args...)` to call `R = do()` whenever f raised an error.

    Parameters
    ----------
    f: Callable[P, T]
      Function being decorated
    do: Callable[Concatenate[Any, P], U]
      Backup function called when `f(...)` raised. First argument will always
      be the exception raised.
    error_type: Any
      Type of the exception we are looking for

    Returns
    -------
    Callable[P, Union[T, U]]
      Callable that decorates f with actions performed AFTER calling it

    """

    def __impl(*args: P.args, **kwargs: P.kwargs) -> Union[T, U]:
        try:
            r = f(*args, **kwargs)
        except error_type as err:
            r = do(err, *args, **kwargs)

        return r

    __impl.__doc__ = "When '{f}' raises {error_type}, do '{do}'".format(
        f=Brief(f),
        error_type=error_type,
        do=Brief(do),
    )

    return __impl
