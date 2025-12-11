#!/usr/bin/env python3

"""Add multiple functional tools to create/handle functors/callables/..."""

from .core import (
    rpartial,
    Brief,
    DoNothing,
    Returns,
    Raises,
)

from .args import (
    ArgAt,
    ForwardArg,
)

from .conditional import (
    When,
    WhenFailing,
)

from .hooks import (
    Before,
    After,
    Decorate,
    HookWrapper,
    hookable,
)

from .sequence import (
    Tee,
    Pipe,
    Yields,
)

from .stringify import (
    StringifyWrapper,
    stringify,
)

__all__ = [
    # core
    "rpartial",
    "Brief",
    "DoNothing",
    "Returns",
    "Raises",
    # args
    "ArgAt",
    "ForwardArg",
    # conditional
    "When",
    "WhenFailing",
    # hooks
    "Before",
    "After",
    "Decorate",
    "HookWrapper",
    "hookable",
    # sequence
    "Tee",
    "Pipe",
    "Yields",
    # stringify
    "StringifyWrapper",
    "stringify",
]
