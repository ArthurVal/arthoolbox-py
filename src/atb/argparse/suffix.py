#!/usr/bin/env python3

"""Utils tools improving argparse suffix handling."""

from dataclasses import (
    dataclass,
)
from functools import (
    update_wrapper,
)

# Typing stuff...
from collections.abc import (
    Callable,
)
from typing import (
    Text,
    Optional,
    TypeVar,
)

T = TypeVar("T")


@dataclass(frozen=True)
class Suffix:
    """Represents a suffix transformation."""

    key: Text
    transform: Callable[[T], T]
    descr: Optional[Text] = None


class Suffixed(object):
    """TODO."""

    def __init__(self, f: Callable[[Text, ...], T], *suffixes: Suffix):
        """TODO."""
        update_wrapper(self, f)
        self.__f = f
        self.__suffixes = suffixes

    @property
    def suffixes(self):
        """TODO."""
        return self.__suffixes

    def With(self, suffix: Suffix):
        """TODO."""
        if not isinstance(suffix, Suffix):
            raise TypeError(f"Wrong suffix type (= {type(suffix)})")

        self.__suffixes += (suffix,)
        return self

    def WithSuffix(
        self,
        key: Text,
        transform: Callable[[T], T],
        descr: Text = None,
    ):
        """TODO."""
        return self.With(Suffix(key=key, transform=transform, descr=descr))

    def GetSuffixFrom(self, s: Text) -> Optional[Suffix]:
        """TODO."""
        # NOTE:
        # We take the largest key in order to avoid string like '10ms' to match
        # 's' as suffix instead of 'ms'
        # In this case, both 's' and 'ms' matches but we take the largest (ms)
        return max(
            # Get ALL suffix(es) found at the end of s
            (suffix for suffix in self.suffixes if s.endswith(suffix.key)),
            # Sort on the length of the suffix's key
            key=lambda suffix: len(suffix.key),
            # When no suffixes:
            default=None,
        )

    def Parse(self, s: Text, *args, **kwargs) -> T:
        """TODO."""
        suffix = self.GetSuffixFrom(s)

        if suffix is None:
            return self.__f(s, *args, **kwargs)

        else:
            return suffix.transform(
                self.__f(s[: -len(suffix.key)], *args, **kwargs)
            )

    def Describe(self, *, sep=", ") -> str:
        """TODO."""
        return sep.join(
            f"{s.key!r}" if s.descr is None else f"{s.key!r} ({s.descr})"
            for s in self.suffixes
        )

    def __call__(self, s: Text, *args, **kwargs) -> T:
        """TODO."""
        return self.Parse(s, *args, **kwargs)

    def __repr__(self) -> str:
        """TODO."""
        return f"Suffixed{{f={self.__f!r}, suffixes={self.suffixes!r}}}"
