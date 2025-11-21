#!/usr/bin/env python3

"""Functional tools like decorators, predicates & co."""

from collections.abc import (
    Callable,
)
from functools import (
    wraps,
)
from sys import (
    exc_info,
)
from typing import (
    Any,
    List,
    Text,
    TypeVar,
)


T = TypeVar("T")


def __get_brief_descr(obj: Any) -> Text:
    return obj.__doc__.partition("\n")[0]


def DoNothing() -> Callable[[...], None]:
    """Creates a functor that does nothing (ignore args & returns None).

    Returns
    -------
    Callable[[...], None]
      A callable that ignore args and do nothing.
    """

    def __impl(*args, **kwargs) -> None:
        """Do nothing"""
        pass

    return __impl


def Returns(v: T) -> Callable[[...], T]:
    """Creates a functor that ALWAYS returns v.

    Parameters
    ----------
    v: T
      Value that will ALWAYS be returned by the underlying functor created

    Returns
    -------
    Callable[[...], T]
      A callable that ignore args ALWAYS returns v.
    """

    def __impl(*args, **kwargs) -> T:
        return v

    __impl.__doc__ = f"Returns {v!r}"

    return __impl


def SequenciallyDo(
    *callables: List[Callable[[...], None]],
) -> Callable[[...], None]:
    """Creates a functor that call each callables with the same args.

    Parameters
    ----------
    *callables: Callable[[...], None]
      All callables called with the same args/kwargs sequencially

    Returns
    -------
    Callable[[...], None]
      A callable that perform the sequencial calls.
    """

    def __impl(*args, **kwargs) -> None:
        for f in callables:
            f(*args, **kwargs)

    __impl.__doc__ = "Sequencially do: {seq}".format(
        seq=", ".join(
            (
                "({i}) {descr!r}".format(
                    i=i,
                    descr=__get_brief_descr(f),
                )
                for i, f in enumerate(callables)
            )
        ),
    )

    return __impl


def Pipe(
    f: Callable[[...], Any],
    *others: List[Callable[[Any], Any]],
) -> Callable[[...], Any]:
    """Creates a functor corresponding to a call pipeline of functions.

    Parameters
    ----------
    f: Callable[[...], Any]
      First function called with args/kwargs
    *others: Callable[[Any], Any]
      others function called with the result of the previous function call

    Returns
    -------
    Callable[[...], Any]
      Functor that perform the pipeline.
    """

    def __impl(*args, **kwargs) -> Any:
        r = f(*args, **kwargs)
        for other in others:
            r = other(r)
        return r

    __impl.__doc__ = "Call pipeline that: {seq}".format(
        seq=" | ".join(
            (
                "({i}) {descr!r}".format(
                    i=i,
                    descr=__get_brief_descr(func),
                )
                for i, func in enumerate([f] + list(others))
            )
        ),
    )

    return __impl


def All(*preds: List[Callable[[...], bool]]) -> Callable[[...], bool]:
    """Predicates corresponding to a logical AND of all the given predicates.

    Parameters
    ----------
    *preds: List[Callable[[...], bool]]
      Predicates called until one of them returns FALSE

    Returns
    -------
    Callable[[...], bool]
      A callable returning a logical AND of all pred(...) calls
    """

    def __impl(*args, **kwargs) -> bool:
        return all((pred(*args, **kwargs) for pred in preds))

    __impl.__doc__ = "ALL of: {}".format(
        ", ".join(
            (
                "({i}) {descr!r}".format(i=i, descr=__get_brief_descr(pred))
                for i, pred in enumerate(preds)
            )
        )
    )

    return __impl


def Any(*preds: List[Callable[[...], bool]]) -> Callable[[...], bool]:
    """Predicates corresponding to a logical OR of all the given predicates.

    Parameters
    ----------
    *preds: List[Callable[[...], bool]]
      Predicates called until one of them returns TRUE

    Returns
    -------
    Callable[[...], bool]
      A callable returning a logical OR of all pred(...) calls
    """

    def __impl(*args, **kwargs) -> bool:
        return any((pred(*args, **kwargs) for pred in preds))

    __impl.__doc__ = "ANY of: {}".format(
        ", ".join(
            (
                "({i}) {descr!r}".format(i=i, descr=__get_brief_descr(pred))
                for i, pred in enumerate(preds)
            )
        )
    )

    return __impl


def DoNot(pred: Callable[[...], bool]) -> Callable[[...], bool]:
    """Predicates corresponding to the negation of pred.

    Parameters
    ----------
    pred: Callable[[...], bool]
      Predicate that we wish to negate

    Returns
    -------
    Callable[[...], bool]
      A callable returning 'not pred(...)'
    """

    def __impl(*args, **kwargs) -> bool:
        return not pred(*args, **kwargs)

    __impl.__doc__ = "Not {descr!r}".format(descr=__get_brief_descr(pred))

    return __impl


def Eq(v: T) -> Callable[[T], bool]:
    """Create a predicates that returns TRUE when arg == v.

    Parameters
    ----------
    v: T
      Value compared to the functor call argument

    Returns
    -------
    Callable[[T], bool]
      A callable returning 'arg == v'
    """

    def __impl(other) -> bool:
        return other == v

    __impl.__doc__ = f"Is Equals to {v!r}"

    return __impl


def Ne(v: T) -> Callable[[T], bool]:
    """Create a predicates that returns TRUE when arg != v.

    Parameters
    ----------
    v: T
      Value compared to the functor call argument

    Returns
    -------
    Callable[[T], bool]
      A callable returning 'arg != v'
    """

    def __impl(other) -> bool:
        return other != v

    __impl.__doc__ = f"Is Not Equals to {v!r}"

    return __impl


def Gt(v: T) -> Callable[[T], bool]:
    """Predicates that returns TRUE when other > v.
    Parameters
    ----------
    v: T
      Value compared to the functor call argument

    Returns
    -------
    Callable[[T], bool]
      A callable returning 'arg > v'
    """

    def __impl(other) -> bool:
        return other > v

    __impl.__doc__ = f"Is Greater than {v!r}"

    return __impl


def Ge(v: T) -> Callable[[T], bool]:
    """Predicates that returns TRUE when other >= v.

    Parameters
    ----------
    v: T
      Value compared to the functor call argument

    Returns
    -------
    Callable[[T], bool]
      A callable returning 'arg >= v'
    """

    def __impl(other) -> bool:
        return other >= v

    __impl.__doc__ = f"Is Greater or Equal than {v!r}"

    return __impl


def Lt(v: T) -> Callable[[T], bool]:
    """Predicates that returns TRUE when other < v.

    Parameters
    ----------
    v: T
      Value compared to the functor call argument

    Returns
    -------
    Callable[[T], bool]
      A callable returning 'arg < v'
    """

    def __impl(other) -> bool:
        return other < v

    __impl.__doc__ = f"Is Less than {v!r}"

    return __impl


def Le(v: T) -> Callable[[T], bool]:
    """Predicates that returns TRUE when other <= v.

    Parameters
    ----------
    v: T
      Value compared to the functor call argument

    Returns
    -------
    Callable[[T], bool]
      A callable returning 'arg <= v'
    """

    def __impl(other) -> bool:
        return other <= v

    __impl.__doc__ = f"Is Less or Equal than {v!r}"

    return __impl


def Before(f: Callable[[...], T], do: Callable[[...], None] = DoNothing()):
    """Decorates `R = f(args...)` to perform actions BEFORE calling f.

    Parameters
    ----------
    f: Callable[[...], T]
      Function being decorated
    do: Callable[[...], None]
      Function called BEFORE f(...)

    Returns
    -------
    Callable[[...], T]
      Callable that decorates f with actions performed BEFORE calling it
    """

    @wraps(f)
    def __wrapper(*args, **kwargs) -> T:
        do(*args, **kwargs)
        return f(*args, **kwargs)

    return __wrapper


def After(
    f: Callable[[...], T],
    on_success: Callable[[T, ...], None] = DoNothing(),
    on_failure: Callable[[...], None] = DoNothing(),
    do: Callable[[...], None] = DoNothing(),
) -> Callable[[...], T]:
    """Decorates `R = f(args...)` to perform actions AFTER calling f.

    Actions performed depends on the initial function call.

    If calling `R = f(args...)` succeeds (i.e. no exception raised), the
    callable `on_success(R, args...)` is called (with its argument corresponding
    to the result `R` and the input args... of f).

    If calling `R = f(args...)` failed (i.e. an exception is raised), the
    callable `on_failure(args...)` is called (with the arguments of f only) and
    the exception is automatically re-raised. User can use `sys.exc_info()` to
    retreive the exception that caused the issue.

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
    f: Callable[[...], T]
      Function being decorated
    on_success: Callable[[T, ...], None]
      Function called AFTER f(...) succeeded
    on_failure: Callable[[Any, ...], None]
      Function called AFTER f(...) raised an exception
    do: Callable[[...], None]
      Function called AFTER f(...), whenever f(...) failed or not

    Returns
    -------
    Callable[[...], T]
      Callable that decorates f with actions performed AFTER calling it
    """

    @wraps(f)
    def __wrapper(*args, **kwargs) -> T:
        try:
            r = f(*args, **kwargs)
        except:
            on_failure(*args, **kwargs)
            raise
        else:
            on_success(r, *args, **kwargs)
        finally:
            do(*args, **kwargs)

        return r

    return __wrapper


def Decorate(
    f: Callable[[...], T],
    before: Callable[[...], None] = DoNothing(),
    after_success: Callable[[T, ...], None] = DoNothing(),
    after_failure: Callable[[...], None] = DoNothing(),
    after: Callable[[...], None] = DoNothing(),
) -> Callable[[...], T]:
    """Creates a decorator that performs actions BEFORE and AFTER calling f.

    Simply corresponds to Before(After(...)...).
    See both Before() and After() for more details.

    Notes
    -----
    Exception raised during the `before()` action won't triggers the
    `after_failure()` calls.

    Parameters
    ----------
    f: Callable[[...], T]
      Function being decorated
    before: Callable[[...], None]
      Function called BEFORE f(...)
    after_success: Callable[[T, ...], None]
      Function called AFTER f(...) succeeded
    after_failure: Callable[[Any, ...], None]
      Function called AFTER f(...) raised an exception
    after: Callable[[...], None]
      Function called AFTER f(...), whenever f(...) failed or not

    Returns
    -------
    Callable[[...], T]
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
