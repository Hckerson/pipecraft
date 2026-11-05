from collections.abc import Mapping
from datetime import datetime
from typing import Annotated
from uuid import uuid4, UUID
from enum import StrEnum

from pydantic import (
    Field,
    EmailStr,
    BaseModel,
    ConfigDict,
    PositiveInt,
    model_serializer,
)
from pydantic.types import UuidVersion


class RunStatus(StrEnum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Run(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: Annotated[UUID, UuidVersion(4)] = Field(default_factory=uuid4)
    started_at: datetime
    finished_at: datetime | None = None
    status: RunStatus = Field(default=RunStatus.RUNNING)
    rows_in: int
    rows_out: int
    error_message: str | None = Field(default=None)


class Row(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int = Field(gt=0)
    name: str = Field(min_length=1)
    email: EmailStr = Field(min_length=1)
    amount: PositiveInt
    created_at: datetime = Field(default_factory=datetime.now)


RawRow = Mapping[str, str | None]
NormalizedRow = dict[str, str | int | datetime | None]
