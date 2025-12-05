#!/usr/bin/env python3

"""Functional tools for any conditional operations."""

from dataclasses import (
    dataclass,
    field,
)
from functools import (
    update_wrapper,
)
import weakref

from collections.abc import (
    Callable,
    Generator,
)
from typing import (
    Concatenate,
    Text,
    Union,
)


@dataclass(frozen=True)
class Hook[**P, R]:
    """TODO."""

    f: Callable[P, R]

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """TODO."""
        return self.f(*args, **kwargs)


class HookList[**P, R]:
    """TODO."""

    def __init__(self) -> None:
        """TODO."""
        self.__hooks = []

    def valid_hooks(self) -> Generator[Hook[P, R]]:
        """Iterate over all the VALID hooks."""
        for ref in self.__hooks:
            hook = ref()
            if hook is not None:
                yield hook

    def cleanup(self) -> None:
        """Cleanup the current hook list be removing invalid hook refs."""
        self.__hooks = list(self.valid_hooks())

    def attach_hook(
        self, hook: Union[Hook[P, R], Callable[P, R]]
    ) -> Hook[P, R]:
        """Attach a new hook to the list.

        Parameters
        ----------
        hook: Union[Hook[Args, R], Callable[Args, R]]
          A callable that we wish to decalre as hook.

        Returns
        -------
        Hook[Args, R]
          An hook object that can be deleted in order to remove it from the
          hook list.
        """
        if not isinstance(hook, Hook):
            hook = Hook(hook)

        self.__hooks.append(weakref.ref(hook))

        return hook

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> list[R]:
        """Call all VALID hooks."""
        return [hook(*args, **kwargs) for hook in self.valid_hooks()]

    def __repr__(self) -> Text:
        """TODO."""
        return "[" + ", ".join(repr(hook) for hook in self.valid_hooks()) + "]"


@dataclass
class Hooks[**P, R]:
    """TODO."""

    pre: HookList[P, None] = field(default_factory=HookList)
    post: HookList[P, None] = field(default_factory=HookList)
    post_success: HookList[Concatenate[R, P], None] = field(
        default_factory=HookList
    )
    post_failure: HookList[Concatenate[Exception, P], None] = field(
        default_factory=HookList
    )


class Hookable[**P, R]:
    """TODO."""

    def __init__(self, f: Callable[P, R]):
        """TODO."""
        self.__hooks = Hooks()
        update_wrapper(self, f)
        self.__f = f

    @property
    def hooks(self) -> Hooks:
        """Get the current hooks."""
        return self.__hooks

    def cleanup(self) -> None:
        """Cleanup all hook lists."""
        [
            hooks.cleanup()
            for hooks in (
                self.hooks.pre,
                self.hooks.post,
                self.hooks.post_success,
                self.hooks.post_failure,
            )
        ]

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """TODO."""
        self.hooks.pre(*args, **kwargs)

        try:
            r = self.__f(*args, **kwargs)

        except Exception as err:
            self.hooks.post_failure(err, *args, **kwargs)
            raise

        else:
            self.hooks.post_success(r, *args, **kwargs)

        finally:
            self.hooks.post(*args, **kwargs)

        return r
