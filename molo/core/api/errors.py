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


class PageNotImportable(Exception):
    '''Raised when attempting to create page.'''

    def __init__(self, message, errors):
        super(PageNotImportable, self).__init__(message)
        self.errors = errors


class ImportedPageNotSavable(Exception):
    '''Raised when attempting to save imported page.'''

    def __init__(self, message, errors):
        super(ImportedPageNotSavable, self).__init__(message)
        self.errors = errors


class ImageInfoListFetchFailed(Exception):
    '''Raised when attempting to save imported page.'''

    def __init__(self, message, errors):
        super(ImageInfoListFetchFailed, self).__init__(message)
        self.errors = errors


class ImageInfoFetchFailed(Exception):
    '''Raised when attempting to save imported page.'''

    def __init__(self, message, errors):
        super(ImageInfoFetchFailed, self).__init__(message)
        self.errors = errors


class ImageCreationFailed(Exception):
    def __init__(self, message, errors):
        super(ImageCreationFailed, self).__init__(message)
        self.errors = errors


class ImportedContentInvalid(Exception):
    def __init__(self, message, errors):
        super(ImportedContentInvalid, self).__init__(message)
        self.errors = errors
