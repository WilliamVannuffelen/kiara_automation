class WorkItemNotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class DataFrameFirstNanIndexTypeError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class AppRefInvalidValueError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class DebugBrowserConnectionError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)