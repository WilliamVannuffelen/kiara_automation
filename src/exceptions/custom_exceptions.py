class InputDataProcessingError(Exception):
    """Base class for exceptions in input data processing."""


class InputFileLoadError(InputDataProcessingError):
    """Exception raised for errors in loading input files."""


class InvalidDataFrameColumnsError(InputDataProcessingError):
    """Exception raised for errors in DataFrame column validation."""


class DataFrameFirstNanIndexTypeError(InputDataProcessingError):
    """Exception raised for type errors in DataFrame first NaN index."""


# split to separate files


class WorkItemNotFoundError(Exception):
    """Exception raised when a work item is not found."""


class AppRefInvalidValueError(Exception):
    """Exception raised for invalid values in app references."""


# move to separate files


class BrowserNavigationError(Exception):
    """Exception raised for errors in browser navigation."""


class PageElementLocatorError(Exception):
    """Exception raised for errors in browser element location."""


class DebugBrowserConnectionError(Exception):
    """Exception raised for errors in browser debugging connection."""


class GeneralTasksNavigationError(BrowserNavigationError):
    """Exception raised for errors in general tasks navigation."""


class TargetElementNotFoundError(PageElementLocatorError):
    """Exception raised when a target item is not found."""
