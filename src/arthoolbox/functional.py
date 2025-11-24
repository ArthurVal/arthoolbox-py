#!/usr/bin/env python3

"""Utils functional tools like decorators & co."""

from collections.abc import (
    Callable,
    Generator,
)
from functools import (
    wraps,
    update_wrapper,
)
from typing import (
    Any,
    NoReturn,
    Text,
    Tuple,
    TypeVar,
    Union,
)


T = TypeVar("T")
U = TypeVar("U")


class WithDescription[T]:
    """Decorator that give the possibility to implement a better/custom repr().

    May be usefull when declaring runtime functions/lambdas and give them a
    better description that changes based on the context.
    """

    def __init__(
        self,
        f: Callable[[...], T],
        descr: Union[
            Text,
            Callable[[Callable[[...], T]], Text],
        ],
    ):
        """Create the WithDescription decorator for the given callable.

        Parameters
        ----------
        f: Callable[[...], T]
          Function being decorated.
        descr: Union[Text, Callable[[Callable[[...], T]],Text]]
          Either a raw description string, that will always be returned whenever
          calling `repr()`.
          OR a callable that handle dynamic `repr()` values, called with `f`
          eveytime in order to create the description.
        """
        self.__f = f
        self.__describe = lambda _: descr if isinstance(descr, Text) else descr
        update_wrapper(self, f)

    def __call__(self, *args, **kwargs) -> T:
        return self.__f(*args, **kwargs)

    def __repr__(self) -> Text:
        return self.__describe(self.__f)


def DoNothing() -> Callable[[...], NoReturn]:
    """Creates a functor that does nothing (ignore args).

    Returns
    -------
    Callable[[...], NoReturn]
      A callable that ignore args and do nothing.
    """

    def __impl(*args, **kwargs) -> NoReturn:
        pass

    return WithDescription(__impl, descr="Do nothing")


def ForwardArgsN(
    *indices: int,
) -> Callable[[...], Union[Tuple[Any, ...], Any, Generator[Any]]]:
    """Creates a functor that forward args.

    Parameters
    ----------
    *indices: int
      If empty (no args given), forwards ALL args.
      If only 1 indices is given, forwards the VALUE `args[i]`.
      If there are more than 1 indices, yields `args[i]`.

    Important
    ---------
    When the indices are out of bound (i.e. `i >= len(args)`), forwards/yields
    `None` instead.

    Returns
    -------
    Callable[[...], Union[Tuple[Any, ...], Any, Generator[Any]]]
      A callable that returns an args filter, based on the indices given.
    """

    # Filter duplicates
    indices = tuple(set(indices))

    if not all(isinstance(i, int) for i in indices):
        raise TypeError(
            "Expecting only integer indices. Got: {wrong}.".format(
                wrong=", ".join(
                    "{v!r} ({t})".format(v=i, t=type(i))
                    for i in indices
                    if not isinstance(i, int)
                )
            )
        )

    def __impl_fwd_all_args(*args) -> Tuple[Any, ...]:
        return args

    def __impl_fwd_one_arg(*args) -> Any:
        return args[indices[0]] if indices[0] < len(args) else None

    def __impl_fwd_mulitple_args(*args) -> Generator[Any]:
        return (args[i] for i in indices if i < len(args))

    if len(indices) == 0:
        return WithDescription(
            f=__impl_fwd_all_args,
            descr="Forwards ALL args",
        )
    elif len(indices) == 1:
        return WithDescription(
            f=__impl_fwd_one_arg,
            descr=f"Forwards ONLY args[{indices[0]}]",
        )
    else:
        return WithDescription(
            f=__impl_fwd_mulitple_args,
            descr=f"Forwards args @ {indices}",
        )


def RemoveArgsN(
    *indices: int,
) -> Callable[[...], Union[Tuple[()], Generator[Any]]]:
    """Creates a functor that remove args.

    Parameters
    ----------
    *indices: int
      If empty, removes ALL args (empty tuple).
      Otherwise, yields `args[i]` for each i that are not in indices.

    Returns
    -------
    Callable[[...], Union[Tuple[], Generator[Any]]]
      A callable that returns an args filter, based on the indices given.
    """

    # Filter duplicates
    indices = set(indices)

    if not all(isinstance(i, int) for i in indices):
        raise TypeError(
            "Expecting only integer indices. Got: {wrong}.".format(
                wrong=", ".join(
                    "{v!r} ({t})".format(v=i, t=type(i))
                    for i in indices
                    if not isinstance(i, int)
                )
            )
        )

    def __impl_rm_all_args(*args) -> Tuple[()]:
        return tuple()

    def __impl_rm_args(*args) -> Generator[Any]:
        return (arg for i, arg in enumerate(args) if i not in indices)

    if len(indices) == 0:
        return WithDescription(
            f=__impl_rm_all_args,
            descr="Remove ALL args",
        )
    else:
        return WithDescription(
            f=__impl_rm_args,
            descr=f"Remove args @ {indices}",
        )


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

    return WithDescription(f=__impl, descr=f"Returns {v!r}")


def Raises(err: T) -> Callable[[...], NoReturn]:
    """Creates a functor that raises err.

    Parameters
    ----------
    err: T
      Error raised

    Returns
    -------
    Callable[[...], NoReturn]
      A callable that ignore args ALWAYS raises err
    """

    def __impl(*args, **kwargs) -> NoReturn:
        raise err

    return WithDescription(f=__impl, descr=f"Raises {err!r}")


def All(*preds: Callable[[...], bool]) -> Callable[[...], bool]:
    """Predicates corresponding to a logical AND of all the given predicates.

    Parameters
    ----------
    *preds: Callable[[...], bool]
      Predicates called until one of them returns FALSE

    Returns
    -------
    Callable[[...], bool]
      A callable returning a logical AND of all pred(...) calls
    """

    def __impl(*args, **kwargs) -> bool:
        return all((pred(*args, **kwargs) for pred in preds))

    return WithDescription(
        f=__impl,
        descr="Returns True when ALL of [{preds!r}]".format(
            preds=", ".join((f"({i}) {pred!r}" for i, pred in enumerate(preds)))
        ),
    )


def Any(*preds: Callable[[...], bool]) -> Callable[[...], bool]:
    """Predicates corresponding to a logical OR of all the given predicates.

    Parameters
    ----------
    *preds: Callable[[...], bool]
      Predicates called until one of them returns TRUE

    Returns
    -------
    Callable[[...], bool]
      A callable returning a logical OR of all pred(...) calls
    """

    def __impl(*args, **kwargs) -> bool:
        return any((pred(*args, **kwargs) for pred in preds))

    return WithDescription(
        f=__impl,
        descr="Returns True when ANY of [{preds!r}]".format(
            preds=", ".join((f"({i}) {pred!r}" for i, pred in enumerate(preds)))
        ),
    )


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

    return WithDescription(f=__impl, descr=f"Return Not {pred!r}")


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

    return WithDescription(f=__impl, descr=f"Is Equal to {v!r}")


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

    return WithDescription(f=__impl, descr=f"Is Not Equal to {v!r}")


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

    return WithDescription(f=__impl, descr=f"Is Greater than {v!r}")


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

    return WithDescription(f=__impl, descr=f"Is Greater or Equal than {v!r}")


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

    return WithDescription(f=__impl, descr=f"Is Less than {v!r}")


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

    return WithDescription(f=__impl, descr=f"Is Less or Equal than {v!r}")


def When(
    pred: Callable[[...], bool],
    do: Callable[[...], T],
    otherwise: Callable[[...], U] = Returns(None),
) -> Callable[[...], Union[T, U]]:
    """Calls either `R = do(..)` or `R = otherwise(...)` based on `pred(...)`

    Parameters
    ----------
    pred: Callable[[...], bool]
      Predicate called with input args.
    do: Callable[[...], U]
      Action done with input args whenever pred returned True
    otherwise: Callable[[...], V]
      Action done with input args whenever pred returned False

    Returns
    -------
    Callable[[...], Union[T, U]]
      A callable that perform a branch returning `do(...)` or `otherwise(...)`
      based on `pred(...)`
    """

    def __impl(*args, **kwargs) -> Union[T, U]:
        return (
            do(*args, **kwargs)
            if pred(*args, **kwargs)
            else otherwise(*args, **kwargs)
        )

    return WithDescription(
        f=__impl,
        descr=(
            "When args '{pred!r}', do '{do!r}'. Otherwise '{otherwise!r}'."
        ).format(
            pred=pred,
            do=do,
            otherwise=otherwise,
        ),
    )


def WhenFailing(
    f: Callable[[...], T],
    do: Callable[[Any, ...], U],
    *,
    error_cls: Any = Exception,
) -> Callable[[...], Union[T, U]]:
    """Decorates `R = f(args...)` to call `R = do()` whenever f raised an error

    Parameters
    ----------
    f: Callable[[...], T]
      Function being decorated
    do: Callable[[Any, ...], U]
      Backup function called when `f(...)` raised. First argument will always be
      the exception raised.
    expected_failure_cls: Any
      Type of the exception we are looking for

    Returns
    -------
    Callable[[...], Union[T, U]]
      Callable that decorates f with actions performed AFTER calling it

    """

    def __impl(*args, **kwargs) -> Union[T, U]:
        try:
            r = f(*args, **kwargs)
        except error_cls as err:
            r = do(err, *args, **kwargs)

        return r

    return __impl


def SequenciallyDo(
    *callables: Callable[[...], NoReturn],
) -> Callable[[...], NoReturn]:
    """Creates a functor that call each callables with the same args.

    Notes
    -----
    The sequence is stopped whenever any callable raises

    Parameters
    ----------
    *callables: Callable[[...], NoReturn]
      All callables called with the same args/kwargs sequencially

    Returns
    -------
    Callable[[...], NoReturn]
      A callable that perform the sequencial calls.
    """

    def __impl(*args, **kwargs) -> NoReturn:
        for f in callables:
            f(*args, **kwargs)

    return WithDescription(
        f=__impl,
        descr="Sequencially do: {seq}".format(
            seq=", ".join((f"({i}) {f!r}" for i, f in enumerate(callables))),
        ),
    )


def Yields(
    *callables: Callable[[...], Any],
) -> Callable[[...], Generator[Any]]:
    """Creates a functor that yields all callables result called with the same args.

    Notes
    -----
    The sequence is stopped whenever any callable raises

    Parameters
    ----------
    *callables: Callable[[...], Any]
      All callables called with the same args/kwargs sequencially

    Returns
    -------
    Callable[[...], NoReturn]
      A callable that perform the sequencial calls.
    """

    def __impl(*args, **kwargs) -> Generator[Any]:
        return (f(*args, **kwargs) for f in callables)

    return WithDescription(
        f=__impl,
        descr="Yields: {seq}".format(
            seq=", ".join((f"({i}) {f!r}" for i, f in enumerate(callables))),
        ),
    )


def Pipe(
    f: Callable[[...], Any],
    *others: Callable[[Any], Any],
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

        for func in others:
            r = func(r)

        return r

    return WithDescription(
        f=__impl,
        descr="Pipeline that: {seq}".format(
            seq=" | ".join(
                (f"({i}) {f!r}" for i, f in enumerate((f,) + others))
            ),
        ),
    )


def Before(
    f: Callable[[...], T],
    do: Callable[[...], NoReturn] = DoNothing(),
):
    """Decorates `R = f(args...)` to perform actions BEFORE calling f.

    Parameters
    ----------
    f: Callable[[...], T]
      Function being decorated
    do: Callable[[...], NoReturn]
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
    on_success: Callable[[T, ...], NoReturn] = DoNothing(),
    on_failure: Callable[[Exception, ...], NoReturn] = DoNothing(),
    do: Callable[[...], NoReturn] = DoNothing(),
) -> Callable[[...], T]:
    """Decorates `R = f(args...)` to perform actions AFTER calling f.

    Actions performed depends on the initial function call.

    If calling `R = f(args...)` succeeds (i.e. no exception raised), the
    callable `on_success(R, args...)` is called (with its argument corresponding
    to the result `R` and the input args... of f).

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
    f: Callable[[...], T]
      Function being decorated
    on_success: Callable[[T, ...], NoReturn]
      Function called AFTER f(...) succeeded
    on_failure: Callable[[Exception, ...], NoReturn]
      Function called AFTER f(...) raised an exception
    do: Callable[[...], NoReturn]
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
    f: Callable[[...], T],
    before: Callable[[...], NoReturn] = DoNothing(),
    after_success: Callable[[T, ...], NoReturn] = DoNothing(),
    after_failure: Callable[[...], NoReturn] = DoNothing(),
    after: Callable[[...], NoReturn] = DoNothing(),
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
    before: Callable[[...], NoReturn]
      Function called BEFORE f(...)
    after_success: Callable[[T, ...], NoReturn]
      Function called AFTER f(...) succeeded
    after_failure: Callable[[Any, ...], NoReturn]
      Function called AFTER f(...) raised an exception
    after: Callable[[...], NoReturn]
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
