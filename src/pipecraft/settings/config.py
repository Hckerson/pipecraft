from typing import Literal

Pattern = Literal["increase", "decrease"]

ERR_MAX_ATTEMPT = 3
ERR_INITIAL_DELAY = 1
ERR_DELAY_PATTERN: Pattern = "increase"
