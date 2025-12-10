#!/usr/bin/env python3

"""Set of functional tools use to ease working with callables/functors/..."""

from functools import (
    wraps,
    update_wrapper,
    partial,
)

from collections.abc import (
    Callable,
)
from typing import (
    Concatenate,
    Text,
    Union,
    ParamSpec,
    TypeVar,
)


P = ParamSpec("P")
R = TypeVar("R")

T = TypeVar("T")
U = TypeVar("U")


class ReprWrapper[**P, R]:
    """Decorator that give the possibility to implement a better/custom repr().

    May be usefull when declaring runtime functions/lambdas and give them a
    better description that changes based on the context.
    """

    def __init__(
        self,
        f: Callable[P, R],
        descr: Union[Text, Callable[[Callable[P, R]], Text]],
    ) -> None:
        """Create the decorator for the given callable.

        Parameters
        ----------
        f: Callable[P, R]
          Function being decorated.
        descr: Union[Text, Callable[[Callable[P, R]],Text]]
          Either a raw description string, that will always be returned
          whenever calling `repr()`.
          OR a callable that handle dynamic `repr()` values, called with `f`
          eveytime in order to create the description.
        """
        update_wrapper(self, f)
        self.__describe = lambda _: descr if isinstance(descr, Text) else descr

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Call the underlying wrapped callable."""
        return self.__wrapped__(*args, **kwargs)

    def __repr__(self) -> Text:
        """Repre the underlying wrapepd callable."""
        return self.__describe(self.__wrapped__)


def with_repr(
    descr: Union[Text, Callable[[Callable[P, R]], Text]],
) -> Callable[[Callable[P, R]], ReprWrapper[P, R]]:
    """Decorate any callable with a custom __repr__.

    Note
    ----
    This is provided to fit the python's `@decorator` syntax. Prefer using
    ReprWrapper direclty if necessary.

    Parameters
    ----------
    descr: Union[Text, Callable[[Callable[P, R]],Text]]
      Either a raw description string, that will always be returned
      whenever calling `repr()`.
      OR a callable that handle dynamic `repr()` values, called with `f`
      eveytime in order to create the description.

    Returns
    -------
    Callable[[Callable[P, R]], ReprWrapper[P, R]]
      Decorator that create a ReprWrapper with the given descr.
    """
    return partial(ReprWrapper, descr=descr)


def DoNothing(*args, **kwargs) -> None:
    """Do Nothing."""
    pass


def Returns(v: T) -> Callable[[...], T]:
    """Create a functor that ALWAYS returns v.

    Parameters
    ----------
    v: T
      Value that will ALWAYS be returned by the underlying functor created

    Returns
    -------
    Callable[[...], T]
      A callable that ignore args and ALWAYS returns v.
    """

    def __impl(*args, **kwargs) -> T:
        return v

    __impl.__doc__ = f"Returns {v!r}"

    return __impl


def Raises(err: T) -> Callable[[...], None]:
    """Create a functor that raises err.

    Parameters
    ----------
    err: T
      Error raised

    Returns
    -------
    Callable[[...], None]
      A callable that ignore args and ALWAYS raises err
    """

    def __impl(*args, **kwargs) -> None:
        raise err

    __impl.__doc__ = f"Raises {err!r}"

    return __impl


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
    on_success: Callable[Concatenate[R, P], None] = DoNothing(),
    on_failure: Callable[Concatenate[Exception, P], None] = DoNothing(),
    do: Callable[P, None] = DoNothing(),
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
    before: Callable[P, None] = DoNothing(),
    after_success: Callable[Concatenate[R, P], None] = DoNothing(),
    after_failure: Callable[Concatenate[Exception, P], None] = DoNothing(),
    after: Callable[P, None] = DoNothing(),
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


def rpartial(f, *args, **kwargs):
    """Do the same as funtools.partial (prepends instead of appending args)."""

    @wraps(f)
    def __wrapper(*fargs, **fkwargs):
        return f(*fargs, *args, **(fkwargs | kwargs))

    return __wrapper
