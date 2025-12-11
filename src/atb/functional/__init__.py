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

from .decorate import (
    Before,
    After,
    Decorate,
)

from .sequence import (
    SequenciallyDo,
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
    # decorate
    "Before",
    "After",
    "Decorate",
    # sequence
    "SequenciallyDo",
    "Pipe",
    "Yields",
    # stringify
    "StringifyWrapper",
    "stringify",
]
