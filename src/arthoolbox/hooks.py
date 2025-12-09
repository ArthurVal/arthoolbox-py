#!/usr/bin/env python3

"""Functional tools for any conditional operations."""

from dataclasses import (
    dataclass,
    field,
)
from functools import (
    update_wrapper,
)

from collections.abc import (
    Callable,
)
from typing import (
    Concatenate,
)


class _HookWrapper[**P, R]:
    """TODO."""

    @dataclass
    class Hooks[**P, R]:
        """TODO."""

        pre: list[Callable[P, None]] = field(default_factory=list)
        post: list[Callable[P, None]] = field(default_factory=list)
        post_success: list[Callable[Concatenate[R, P], None]] = field(
            default_factory=list
        )
        post_failure: list[Callable[Concatenate[Exception, P], None]] = field(
            default_factory=list
        )

    def __init__(self, f: Callable[P, R]):
        """TODO."""
        self.hooks = _HookWrapper.Hooks()

        self.__f = f
        update_wrapper(self, f)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """TODO."""
        for f in self.hooks.pre:
            f(*args, **kwargs)

        try:
            r = self.__f(*args, **kwargs)

        except Exception as err:
            for f in self.hooks.post_failure:
                f(err, *args, **kwargs)

            raise

        else:
            for f in self.hooks.post_success:
                f(r, *args, **kwargs)

        finally:
            for f in self.hooks.post:
                f(*args, **kwargs)

        return r


def hookable():
    """TODO."""
    return _HookWrapper
