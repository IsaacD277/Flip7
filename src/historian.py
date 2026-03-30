
""" historian.py
----------------
Undo/redo manager

Original Source: https://github.com/ffomezolam/historian-py/blob/master/historian.py
"""

from collections import deque
from typing import Optional

class Historian:
    """
    The undo/redo manager class

    Parameters
    ----------
    limit: int
        maximum size of undo stack

    Examples
    --------

    # create an instance of Historian
    H = Historian()

    # start with a variable to manipulate
    # and functions to manipulate it
    a = 5

    def inc(n):
        global a
        a += n
        H.register(dec, n) # register inverse function!

    def dec(n):
        global a
        a -= n
        H.register(inc, n) # register inverse function!

    # now run some commands
    inc(5) # a is now 10
    dec(2) # a is now 8
    dec(4) # a is now 4
    inc(3) # a is now 7

    # and we can undo/redo these at will
    H.undo() # a undoes one step to 4
    H.undo() # a undoes one step to 8
    H.redo() # a redoes one step to 4

    # repeat ad nauseum
    """

    def __init__(self, limit: Optional[int] = None):
        self._limit = limit
        self._history = {
            "undo": deque(maxlen = limit),
            "redo": deque(maxlen = limit)
        }
        self._next = "undo"

    def register(self, command, *args, **kwargs):
        "Register a command with the historian."

        kind = self._next

        self._history[kind].append((command, args, kwargs))

        self._next = "undo"

        return self

    def _do(self, kind: str, n: int = 1):
        "Mechanics for undo/redo"

        limit = self._limit or len(self._history[kind])

        n = limit if not n or abs(n) > limit else abs(n)

        if n > len(self._history[kind]): n = len(self._history[kind])

        for _ in range(n):
            # get command data
            cmd, args, kwargs = self._history[kind].pop()

            # set inverse as next registration stack
            self._next = "redo" if kind == "undo" else "undo"

            # run command
            cmd(*args, **kwargs)

        return self

    def undo(self, n: int = 1):
        "Undo the last command(s)"

        return self._do("undo", n)

    def redo(self, n: int = 1):
        "Redo the last command(s)"

        return self._do("redo", n)

    def clear(self, kinds: str|tuple = ("undo", "redo")):
        "Clear history"
        if type(kinds) == str: kinds = (kinds,)
        for kind in kinds:
            self._history[kind].clear()

        return self

    def size(self, kind: str = "undo"):
        "Get history size"
        return len(self._history[kind])

class HistorianMixin:
    """
    Historian mixin class
    """

    def __init__(self, limit: int = 10):
        self._undomgr = Historian(limit)

    def undo(self, n: int = 1):
        self._undomgr.undo(n)
        return self

    def redo(self, n: int = 1):
        self._undomgr.redo(n)
        return self