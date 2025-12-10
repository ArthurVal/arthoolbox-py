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
    Any,
    Text,
    Union,
    Concatenate,
    ParamSpec,
    TypeVar,
)


P = ParamSpec("P")
R = TypeVar("R")

T = TypeVar("T")
U = TypeVar("U")


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
