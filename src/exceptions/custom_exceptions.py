class InputDataProcessingError(Exception):
    """Base class for exceptions in input data processing."""


class InputFileLoadError(InputDataProcessingError):
    """Exception raised for errors in loading input files."""


class InvalidDataFrameColumnsError(InputDataProcessingError):
    """Exception raised for errors in DataFrame column validation."""


class DataFrameFirstNanIndexTypeError(InputDataProcessingError):
    """Exception raised for type errors in DataFrame first NaN index."""


class WorkItemNotFoundError(Exception):
    """Exception raised when a work item is not found."""


class AppRefInvalidValueError(Exception):
    """Exception raised for invalid values in app references."""


class DebugBrowserConnectionError(Exception):
    """Exception raised for errors in browser debugging connection."""
