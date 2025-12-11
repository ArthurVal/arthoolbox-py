#!/usr/bin/env python3

"""Functional tools to add hook capabilities to any callable."""

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
    ParamSpec,
    TypeVar,
)


@dataclass(frozen=True)
class Hooks[R, **P]:
    """Container for all different hook available."""

    pre: list[Callable[P, None]] = field(default_factory=list)
    post: list[Callable[P, None]] = field(default_factory=list)
    post_success: list[Callable[Concatenate[R, P], None]] = field(
        default_factory=list
    )
    post_failure: list[Callable[Concatenate[Exception, P], None]] = field(
        default_factory=list
    )


class HookWrapper[R, **P]:
    """Decorator that wraps any callable with hooks.

    The hooks can be updated through the `.hooks` attributs, giving access to
    list of hooks called based on the hook type.

    Currently, the hooks available are:
    - "pre": Hook called BEFORE calling the underlying wrapped function;
    - "post": Hook called AFTER calling the underlying wrapped function
      (whether it failed or not);
    - "post_success": Hook called AFTER a SUCCESSFULL call to the underlying
      wrapped function;
    - "post_failure": Hook called AFTER a FAILED call to the underlying
      wrapped function;

    All hooks are called with the same arguments given to the underlying wrapped
    function. Additionally, "post_success" and "post_failure" are called with
    the value returned (respectively exception raised) by the wrapped function
    as 1rst argument.

    Example
    -------
    >>> my_print = HookWrapper(print)
    >>> my_print("Hello")
    Hello
    >>> my_print.hooks
    Hooks(pre=[], post=[], post_success=[], post_failure=[])
    >>> my_print.hooks.pre.append(
    ...     lambda *args, **kwargs: print(f"Pre: {args} {kwargs}")
    ... )
    >>> my_print.hooks
    Hooks(pre=[<function <lambda> at 0x7a7823347b00>], post=[], post_success=[], post_failure=[])
    >>> my_print("Hello")
    Pre: ('Hello',) {}
    Hello
    """

    def __init__(self, f: Callable[P, R]):
        """Construct the wrapper from a given callable."""
        update_wrapper(self, f)
        self.__hooks = Hooks()

    @property
    def hooks(self) -> Hooks:
        """Access the underlying hooks."""
        return self.__hooks

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Call the wrapped callable with its defined hooks."""
        for f in self.hooks.pre:
            f(*args, **kwargs)

        try:
            r = self.__wrapped__(*args, **kwargs)

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


def hookable[R, **P](f: Callable[P, R]) -> HookWrapper[R, P]:
    """Decorate any callable with hooks.

    See HookWrapper for more details.
    """
    return HookWrapper[R, P](f)
