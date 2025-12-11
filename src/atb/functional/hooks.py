#!/usr/bin/env python3

"""Functional tools to add hook capabilities to any callable."""

from .core import (
    DoNothing,
)

from dataclasses import (
    dataclass,
    field,
)
from functools import (
    update_wrapper,
    wraps,
)

from collections.abc import (
    Callable,
)
from typing import (
    Concatenate,
    ParamSpec,
    TypeVar,
    Generic,
)

P = ParamSpec("P")
R = TypeVar("R")


def Before(f: Callable[P, R], do: Callable[P, None]):
    """Decorate `R = f(args...)` to perform actions BEFORE calling f.

    Parameters
    ----------
    f: Callable[P, R]
      Function being decorated
    do: Callable[P, NoReturn]
      Function called BEFORE f(...)

    Returns
    -------
    Callable[P, R]
      Callable that decorates f with actions performed BEFORE calling it
    """

    @wraps(f)
    def __wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        do(*args, **kwargs)
        return f(*args, **kwargs)

    return __wrapper


def After(
    f: Callable[P, R],
    on_success: Callable[Concatenate[R, P], None] = DoNothing,
    on_failure: Callable[Concatenate[Exception, P], None] = DoNothing,
    do: Callable[P, None] = DoNothing,
) -> Callable[P, R]:
    """Decorate `R = f(args...)` to perform actions AFTER calling f.

    Actions performed depends on the initial function call.

    If calling `R = f(args...)` succeeds (i.e. no exception raised), the
    callable `on_success(R, args...)` is called (with its argument
    corresponding to the result `R` and the input args... of f).

    If calling `R = f(args...)` failed (i.e. an exception is raised), the
    callable `on_failure(Err, args...)` is called (with the Exception `Err`
    raised and the arguments of f only). The exception `Err` is automatically
    re-raised afterwards.

    In any case (failure or not), `do(args...)` will be called AFTER the above
    calls.

    Important
    ---------
    - do(args...) is ALWAYS called AFTER do_success() and do_failure(),
      whenever an exception is raised or not;
    - if an exception is caught, it will be automatically re-raised after
      calling do_failure();

    Parameters
    ----------
    f: Callable[P, R]
      Function being decorated
    on_success: Callable[Concatenate[R, P], NoReturn]
      Function called AFTER f(...) succeeded
    on_failure: Callable[Concatenate[Exception, P], NoReturn]
      Function called AFTER f(...) raised an exception
    do: Callable[P, NoReturn]
      Function called AFTER f(...), whenever f(...) failed or not

    Returns
    -------
    Callable[P, R]
      Callable that decorates f with actions performed AFTER calling it
    """

    @wraps(f)
    def __wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            r = f(*args, **kwargs)
        except Exception as err:
            on_failure(err, *args, **kwargs)
            raise
        else:
            on_success(r, *args, **kwargs)
        finally:
            do(*args, **kwargs)

        return r

    return __wrapper


def Decorate(
    f: Callable[P, R],
    before: Callable[P, None] = DoNothing,
    after_success: Callable[Concatenate[R, P], None] = DoNothing,
    after_failure: Callable[Concatenate[Exception, P], None] = DoNothing,
    after: Callable[P, None] = DoNothing,
) -> Callable[P, R]:
    """Create a decorator that performs actions BEFORE and AFTER calling f.

    Simply corresponds to Before(After(...)...).
    See both Before() and After() for more details.

    Notes
    -----
    Exception raised during the `before()` action won't triggers the
    `after_failure()` calls.

    Parameters
    ----------
    f: Callable[P, R]
      Function being decorated
    before: Callable[P, None]
      Function called BEFORE f(...)
    after_success: Callable[Concatenate[R, P], None]
      Function called AFTER f(...) succeeded
    after_failure: Callable[Concatenate[Exception, P], None]
      Function called AFTER f(...) raised an exception
    after: Callable[P, None]
      Function called AFTER f(...), whenever f(...) failed or not

    Returns
    -------
    Callable[P, R]
      Callable that decorates f that perform PRE & POST actions
    """
    return Before(
        f=After(
            f=f,
            do=after,
            on_success=after_success,
            on_failure=after_failure,
        ),
        do=before,
    )


@dataclass(frozen=True)
class Hooks(Generic[P, R]):
    """Container for all different hook available."""

    pre: list[Callable[P, None]] = field(default_factory=list)
    post: list[Callable[P, None]] = field(default_factory=list)
    post_success: list[Callable[Concatenate[R, P], None]] = field(
        default_factory=list
    )
    post_failure: list[Callable[Concatenate[Exception, P], None]] = field(
        default_factory=list
    )


class HookWrapper(Generic[P, R]):
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
        self.__hooks = Hooks[P, R]()

    @property
    def hooks(self) -> Hooks[P, R]:
        """Access the underlying hooks."""
        return self.__hooks

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Call the wrapped callable with its defined hooks."""
        for f in self.hooks.pre:
            f(*args, **kwargs)

        try:
            r: R = self.__wrapped__(*args, **kwargs)

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


def hookable(f: Callable[P, R]) -> HookWrapper[R, P]:
    """Decorate any callable with hooks.

    See HookWrapper for more details.
    """
    return HookWrapper[R, P](f)
