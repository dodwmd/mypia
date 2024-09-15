class MyPIAException(Exception):
    """Base exception class for MyPIA"""
    pass


class DatabaseError(MyPIAException):
    """Raised when a database operation fails"""
    pass


class APIError(MyPIAException):
    """Raised when an API request fails"""
    pass


class ConfigurationError(MyPIAException):
    """Raised when there's an issue with the configuration"""
    pass


class AuthenticationError(MyPIAException):
    """Raised when authentication fails"""
    pass
