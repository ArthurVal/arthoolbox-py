#!/usr/bin/env python3

"""Add multiple functional tools to create/handle functors/callables/..."""

from .core import (
    DoNothing,
    Returns,
    Raises,
    Before,
    After,
    Decorate,
    rpartial,
    StringifyWrapper,
    stringify,
)

from .args import (
    ArgAt,
    ForwardArg,
)

from .conditional import (
    When,
    WhenFailing,
)

from .sequence import (
    SequenciallyDo,
    Pipe,
    Yields,
)

__all__ = [
    # core
    "DoNothing",
    "Returns",
    "Raises",
    "Before",
    "After",
    "Decorate",
    "rpartial",
    "StringifyWrapper",
    "stringify",
    # args
    "ArgAt",
    "ForwardArg",
    # conditional
    "When",
    "WhenFailing",
    # sequence
    "SequenciallyDo",
    "Pipe",
    "Yields",
]
