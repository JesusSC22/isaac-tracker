class SaveNotFoundError(Exception):
    """No persistentgamedata*.dat found in expected locations."""


class SaveParseError(Exception):
    """Raised when a save file cannot be parsed."""

    def __init__(self, message: str, path: str | None = None):
        super().__init__(message)
        self.path = path
