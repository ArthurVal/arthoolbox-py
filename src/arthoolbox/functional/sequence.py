#!/usr/bin/env python3

"""Set of functional tools to create pipelines/sequence/..."""

from .core import (
    Brief,
)

from collections.abc import (
    Callable,
    Generator,
)
from typing import (
    Any,
    ParamSpec,
)

P = ParamSpec("P")


def SequenciallyDo(*callables: Callable[P, None]) -> Callable[P, None]:
    """Create a functor that call each callables with the same args.

    Notes
    -----
    - All callables are called with the same args;
    - The sequence is stopped whenever any callable raises;
    - Return value(s) are ignored (use `Yields()` to yield return values).

    Parameters
    ----------
    *callables: Callable[P, None]
      All callables called with the same args/kwargs sequencially

    Returns
    -------
    Callable[P, NoReturn]
      A callable that perform the sequencial calls.
    """

    def __impl(*args: P.args, **kwargs: P.kwargs) -> None:
        for f in callables:
            f(*args, **kwargs)

    __impl.__doc__ = "Sequencially do: {seq}".format(
        seq=", ".join((f"({i}) {Brief(f)}" for i, f in enumerate(callables)))
    )

    return __impl


def Yields(*callables: Callable[P, Any]) -> Callable[P, Generator[Any]]:
    """Create a functor that yields all callables' result sequencially.

    Notes
    -----
    - All callables are called with the same args;
    - The sequence is stopped whenever any callable raises.

    Parameters
    ----------
    *callables: Callable[P, Any]
      All callables called with the same args/kwargs sequencially

    Returns
    -------
    Callable[P, Generator[Any]]
      A callable that sequencially yields all callables' result called using
      the same input args.
    """

    def __impl(*args: P.args, **kwargs: P.kwargs) -> Generator[Any]:
        return (f(*args, **kwargs) for f in callables)

    __impl.__doc__ = "Yields: {seq}".format(
        seq=", ".join((f"({i}) {Brief(f)}" for i, f in enumerate(callables)))
    )

    return __impl


def Pipe(
    f: Callable[P, Any],
    *others: Callable[[Any], Any],
) -> Callable[P, Any]:
    """Create a functor corresponding to a call pipeline of functions.

    Parameters
    ----------
    f: Callable[P, Any]
      First function called with all args/kwargs
    *others: Callable[[Any], Any]
      others function called with the result of the previous function call

    Returns
    -------
    Callable[P, Any]
      Functor that perform the pipeline.
    """

    def __impl(*args: P.args, **kwargs: P.kwargs) -> Any:
        r = f(*args, **kwargs)

        for func in others:
            r = func(r)

        return r

    __impl.__doc__ = "Pipeline that: {seq}".format(
        seq=" | ".join(
            (f"({i}) {Brief(f)}" for i, f in enumerate((f,) + others))
        ),
    )

    return __impl
