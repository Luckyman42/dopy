class DopyException(Exception):
    """Base Exception for dopy"""


class CommandNotFoundException(DopyException):
    """Raised when a command is not found"""


class InvalidCommandArgumentsException(DopyException):
    """Raised when command arguments are invalid"""
