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
    stability:experimental stability:new area:utils
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


class DataProcessor:
    """Process data records.

    Badges
    ------
    stability:stable area:core

    Parameters
    ----------
    config : dict
        Configuration mapping.
    """

    def __init__(self, config):
        self.config = config

    def run(self, data):
        """Execute the processing pipeline.

        Parameters
        ----------
        data : list
            Input records.

        Returns
        -------
        list
            Processed records.

        Badges
        ------
        stability:stable area:core
        """
        return data

    def preview(self, data, n=5):
        """Return a beta preview of processed output.

        Parameters
        ----------
        data : list
            Input records.
        n : int, optional
            Number of preview items.  Default is ``5``.

        Returns
        -------
        list

        Badges
        ------
        stability:beta area:core
        """
        return data[:n]
