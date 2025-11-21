#!/usr/bin/env python3

"""Utils functional tools like decorators & co."""

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
    """Creates a functor that does nothing (ignore args & returns None)."""

    def __impl(*args, **kwargs) -> None:
        """Do nothing"""
        pass

    return __impl


def Returns(v: T) -> Callable[[...], T]:
    """Creates a functor that ALWAYS returns v."""

    def __impl(*args, **kwargs) -> T:
        return v

    __impl.__doc__ = f"Returns {v!r}"

    return __impl


def SequenciallyDo(
    f: Callable[[...], Any],
    *others: List[Callable[[Any], Any]],
    chain: bool = True,
) -> Callable[[...], Any]:
    """Creates a functor that f and then others in sequence."""

    def __impl_chain(*args, **kwargs) -> Any:
        r = f(*args, **kwargs)
        for other in others:
            r = other(r)
        return r

    def __impl_no_chain(*args, **kwargs) -> None:
        f(*args, **kwargs)

        for other in others:
            other(*args, **kwargs)

    __impl = __impl_chain if chain else __impl_no_chain
    __impl.__doc__ = "Sequencially do: {seq}".format(
        seq="{}".format(" -> " if chain else ", ").join(
            (
                "({i}) {descr!r}".format(
                    i=i,
                    descr=__get_brief_descr(other),
                )
                for i, other in enumerate([f] + list(others))
            )
        ),
    )

    return __impl


def Eq(v: T) -> Callable[[T], bool]:
    """Predicates that returns TRUE when other == v."""

    def __impl(other) -> bool:
        return other == v

    __impl.__doc__ = f"Is Equals to {v!r}"

    return __impl


def Gt(v: T) -> Callable[[T], bool]:
    """Predicates that returns TRUE when other > v."""

    def __impl(other) -> bool:
        return other > v

    __impl.__doc__ = f"Is Greater than {v!r}"

    return __impl


def Ge(v: T) -> Callable[[T], bool]:
    """Predicates that returns TRUE when other >= v."""

    def __impl(other) -> bool:
        return other >= v

    __impl.__doc__ = f"Is Greater or Equal than {v!r}"

    return __impl


def Lt(v: T) -> Callable[[T], bool]:
    """Predicates that returns TRUE when other < v."""

    def __impl(other) -> bool:
        return other < v

    __impl.__doc__ = f"Is Less than {v!r}"

    return __impl


def Le(v: T) -> Callable[[T], bool]:
    """Predicates that returns TRUE when other <= v."""

    def __impl(other) -> bool:
        return other <= v

    __impl.__doc__ = f"Is Less or Equal than {v!r}"

    return __impl


def All(*preds: List[Callable[[...], bool]]) -> Callable[[...], bool]:
    """Predicates corresponding to a logical AND of all the given predicates."""

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
    """Predicates corresponding to a logical OR of all the given predicates."""

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
    """Predicates corresponding to the negation of pred."""

    def __impl(*args, **kwargs) -> bool:
        return not pred(*args, **kwargs)

    __impl.__doc__ = "Not {descr!r}".format(descr=__get_brief_descr(pred))

    return __impl


def Before(f: Callable[[...], T], do: Callable[[...], None] = DoNothing()):
    """Creates a decorator that calls do(args...) AND THEN return f(args...)."""

    @wraps(f)
    def __wrapper(*args, **kwargs) -> T:
        do(*args, **kwargs)
        return f(*args, **kwargs)

    return __wrapper


def After(
    f: Callable[[...], T],
    do: Callable[[...], None] = DoNothing(),
    on_success: Callable[[T, ...], None] = DoNothing(),
    on_failure: Callable[[Any, ...], None] = DoNothing(),
) -> Callable[[...], T]:
    """Creates a decorator that calls f(args...) AND THEN do(args...).

    Additionnaly:
    - do_success(R, args...) will be called with the result R of R = f(args...)
      if no exception is raised;
    - do_failure(sys.exec_info(), args...) will be called when f(args...) raised
      an exception;

    Note:
    - do(args...) is ALWAYS called AFTER do_success() and do_failure(),
      whenever an exception is raised or not;
    - if an exception is caught, it will be automatically re-raised after
      calling do_failure();
    """

    @wraps(f)
    def __wrapper(*args, **kwargs) -> T:
        try:
            r = f(*args, **kwargs)
        except:
            on_failure(exc_info(), *args, **kwargs)
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
    after: Callable[[...], None] = DoNothing(),
    after_success: Callable[[T, ...], None] = DoNothing(),
    after_failure: Callable[[Any, ...], None] = DoNothing(),
) -> Callable[[...], T]:
    """Creates a decorator that performs actions BEFORE and AFTER calling f."""
    return Before(
        f=After(
            f=f,
            do=after,
            on_success=after_success,
            on_failure=after_failure,
        )
        do=before,
    )
