#!/usr/bin/env python3

"""Add multiple functional tools to create/handle functors/callables/..."""

from .core import (
    ReprWrapper,
    with_repr,
    DoNothing,
    Returns,
    Raises,
    Before,
    After,
    Decorate,
    rpartial,
)

from .args import (
    AtIdx,
    WithKey,
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
    "ReprWrapper",
    "with_repr",
    "DoNothing",
    "Returns",
    "Raises",
    "Before",
    "After",
    "Decorate",
    "rpartial",
    # args
    "AtIdx",
    "WithKey",
    "ForwardArg",
    # conditional
    "When",
    "WhenFailing",
    # sequence
    "SequenciallyDo",
    "Pipe",
    "Yields",
]
