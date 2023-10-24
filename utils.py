class EventAdditionError(Exception):
    """
    Custom exception to signal issues when trying to add events.
    
    Attributes:
        message (str): Descriptive message for the error.
    """
    def __init__(self, message) -> None:
        super().__init__(message)