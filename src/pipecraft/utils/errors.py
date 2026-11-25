from pipecraft.settings.config import ERR_RETRYABLE_CODES


class PipelineError(Exception):
    pass


class ParseError(Exception):
    pass


class DbError(Exception):
    def __init__(self, message: str, sqlite_errorcode: int | None = None) -> None:
        super().__init__(message)
        self.sqlite_errorcode = sqlite_errorcode


class RowTransformError(ValueError):
    pass


def process_error(error: Exception) -> bool:
    return isinstance(error, DbError) and error.sqlite_errorcode in ERR_RETRYABLE_CODES
