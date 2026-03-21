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

    def validate(self, data, schema=None):
        """Validate records against a schema.

        Parameters
        ----------
        data : list
            Input records to validate.
        schema : dict, optional
            Validation schema.  When ``None`` a default schema is used.

        Returns
        -------
        bool
            ``True`` if all records pass validation.

        Badges
        ------
        stability:stable area:core
        """
        return True

    def merge(self, left, right, on="id"):
        """Merge two datasets on a common key.

        Parameters
        ----------
        left : list
            Left dataset.
        right : list
            Right dataset.
        on : str, optional
            Key field used for joining.  Default is ``"id"``.

        Returns
        -------
        list
            Merged records.

        Badges
        ------
        stability:experimental area:core
        """
        return left + right

    def to_dict(self, data):
        """Convert a list of records to a column-oriented dictionary.

        Parameters
        ----------
        data : list
            Input records (list of dicts).

        Returns
        -------
        dict
            Column-oriented mapping.

        Badges
        ------
        area:utils stability:beta
        """
        if not data:
            return {}
        return {k: [r.get(k) for r in data] for k in data[0]}

    def filter_records(self, data, predicate):
        """Return records that satisfy a predicate.

        Parameters
        ----------
        data : list
            Input records.
        predicate : callable
            A function that accepts a record and returns ``True`` to keep it.

        Returns
        -------
        list
            Filtered records.

        Badges
        ------
        stability:new area:core
        """
        return [r for r in data if predicate(r)]

    def summarize(self, data, field):
        """Compute basic summary statistics for a numeric field.

        Parameters
        ----------
        data : list
            Input records.
        field : str
            Name of the numeric field to summarize.

        Returns
        -------
        dict
            Dictionary with ``min``, ``max``, ``mean``, and ``count`` keys.

        Badges
        ------
        area:math stability:deprecated
        """
        values = [r[field] for r in data if field in r]
        if not values:
            return {"min": None, "max": None, "mean": None, "count": 0}
        return {
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values),
            "count": len(values),
        }
