"""Example library used to demonstrate sphinx-badges autodoc integration.

All public objects carry a numpy-style ``Badges`` section using the
``group:name`` syntax.  sphinx-badges parses and renders these automatically.
"""


class DataProcessor:
    """Process data records.

    Note
    ----
    Just a sample class

    Parameters
    ----------
    config : dict
        Configuration mapping.

    Badges
    ------
    stability:stable area:core platform:web
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
