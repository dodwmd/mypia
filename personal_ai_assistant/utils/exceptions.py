class MyPIAException(Exception):
    """Base exception class for MyPIA"""
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ConfigurationError(MyPIAException):
    """Raised when there's a configuration error"""
    pass

class DatabaseError(MyPIAException):
    """Raised when there's a database-related error"""
    pass

class NetworkError(MyPIAException):
    """Raised when there's a network-related error"""
    pass

class APIError(MyPIAException):
    """Raised when there's an API-related error"""
    pass

class TaskExecutionError(MyPIAException):
    """Raised when there's an error executing a task"""
    pass
