class PipelineError(Exception):
    pass


class ParseError(Exception):
    pass


class DbError(Exception):
    pass


class RowTransformError(ValueError):
    pass


def process_error(error: Exception) -> bool:
    return isinstance(error, DbError)
