'''
Custom exceptions to use throughout project.
'''

class ContentFormatException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

class ItemNotFound(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

class DatabaseConnectionError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

class InvalidDatabaseOperation(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)
