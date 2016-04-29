class ImportError(Exception):
    """Raised when there is an error importing"""


class InvalidParametersError(Exception):
    """Raised when the parameters given to the import api are invalid"""

    def __init__(self, message, errors):
        super(InvalidParametersError, self).__init__(message)
        self.errors = errors


class SiteResponseError(Exception):
    """
    Raised if we could not retrieve repo summaries from a given site url.
    """
