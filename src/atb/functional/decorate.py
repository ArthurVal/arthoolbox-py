#!/usr/bin/env python3

"""Set of functional tools use to decorate callables/functors/..."""

from .core import (
    DoNothing,
)

from functools import (
    wraps,
)

from collections.abc import (
    Callable,
)
from typing import (
    Concatenate,
    ParamSpec,
    TypeVar,
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
