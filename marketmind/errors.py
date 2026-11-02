"""Research workflow errors safe to report through the API."""

class ResearchUnavailable(Exception):
    """Missing configuration or insufficient market evidence."""

class SynthesisError(Exception):
    """Provider failed or returned an invalid research report."""
