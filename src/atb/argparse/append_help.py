#!/usr/bin/env python3

"""TODO."""

import argparse
from typing import (
    Text,
)


def AppendHelpWithDefault(
    action: argparse.Action,
    *,
    fmt: Text = "\n(default: {default!r})",
) -> argparse.Action:
    r"""Append the given argparse action help with its default value.

    Parameters
    ----------
    action: argparse.Action
      Action created by .add_argument()
    fmt: Text
      The format of the help string (default to "\n(default: {default!r})")

    Returns
    -------
    T
      The action updated
    """
    if hasattr(action, "default") and hasattr(action, "help"):
        action.help += fmt.format(default=action.default)

    return action
