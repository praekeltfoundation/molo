class RecordOverwriteError(Exception):
    '''Raised when attempting to overwrite existing recorded relationships.'''

    def __init__(self, message, errors):
        super(RecordOverwriteError, self).__init__(message)
        self.errors = errors


class ReferenceUnimportedContent(Exception):
    '''Raised when referencing content that has not been imported.'''

    def __init__(self, message, errors):
        super(ReferenceUnimportedContent, self).__init__(message)
        self.errors = errors
