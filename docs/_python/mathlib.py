"""Example library used to demonstrate sphinx-badges autodoc integration.

All public objects carry a numpy-style ``Badges`` section using the
``group:name`` syntax.  sphinx-badges parses and renders these automatically.
"""


def add(x, y):
    """Return the sum of *x* and *y*.

    Parameters
    ----------
    x : float
        First operand.
    y : float
        Second operand.

    Returns
    -------
    float
        The sum.

    Badges
    ------
    stability:stable area:math
    """
    return x + y


def experimental_sort(items, *, reverse=False):
    """Sort *items* using an experimental in-place algorithm.

    Parameters
    ----------
    items : list
        The list to sort (modified in place).
    reverse : bool, optional
        Sort in descending order.  Default is ``False``.

    Returns
    -------
    list
        The sorted list (same object as *items*).

    Badges
    ------
    area:utils stability:stable  stability:beta stability:experimental
    """
    items.sort(reverse=reverse)
    return items


def legacy_format(value):
    """Format *value* as a string using the old formatting rules.

    .. deprecated:: 0.1.0
       Use :func:`add` and format the result yourself.

    Parameters
    ----------
    value : object
        Any object that supports ``str()``.

    Returns
    -------
    str

    Badges
    ------
    stability:deprecated area:utils
    """
    return str(value)
