from .source import ParseError
from .transforms import RowTransformError
from pipecraft.utils import DbError










def process_error(err:Exception) -> bool:

    match err:
        case ParseError():
            return False
        case RowTransformError():
            return False
        case DbError():
            return True
        case _:
            return False