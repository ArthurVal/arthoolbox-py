#!/usr/bin/env python3

"""Set of functional tools to stringify callables/functors/..."""

from .core import (
    Brief,
    Returns,
)

from functools import (
    update_wrapper,
    partial,
)

from collections.abc import (
    Callable,
)
from typing import (
    Text,
    Union,
    ParamSpec,
    TypeVar,
)


P = ParamSpec("P")
R = TypeVar("R")


class StringifyWrapper:
    """Wrapper that give the possibility to implement a better/custom str().

    May be usefull when declaring runtime functions/lambdas and give them a
    better description that changes based on the context.
    """

    def __init__(
        self,
        f: Callable[P, R],
        to_str: Union[Text, Callable[[Callable[P, R]], Text]],
    ) -> None:
        """Create the wrapper adding a custom __str__.

        Parameters
        ----------
        f: Callable[P, R]
          Wrapped function being decorated.
        to_str: Union[Text, Callable[[Callable[P, R]],Text]]
          Either a raw string, that will always be returned whenever calling
          `str()`, OR, a callable that handle dynamic `str()` values, called
          with `f` eveytime in order to create the description dynamically.
        """
        update_wrapper(self, f)
        self.__to_str = Returns(to_str) if isinstance(to_str, Text) else to_str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Call the underlying wrapped callable."""
        return self.__wrapped__(*args, **kwargs)

    def __str__(self) -> Text:
        """Stringify the underlying wrapped callable."""
        return self.__to_str(self.__wrapped__)

    def __repr__(self) -> Text:
        """Repr of the StringifyWrapper."""
        return "StringifyWrapper(f={f}, to_str={to_str})".format(
            f=repr(self.__wrapped__),
            to_str=Brief(self.__to_str),
        )


def stringify(
    s: Union[Text, Callable[[Callable[P, R]], Text]],
) -> StringifyWrapper:
    """Decorate a function to add a custom __str__() function.

    Parameters
    ----------
    s: Union[Text, Callable[[Callable[P, R]],Text]]
      Either a raw string, that will always be returned whenever calling
      `str()`, OR, a function that handle dynamic `str()` values, called
      with the function eveytime in order to create the description dynamically

    Returns
    -------
    StringifyWrapper
      A wrapper use to decorate any callable/function.
    """
    return partial(StringifyWrapper, to_str=s)
