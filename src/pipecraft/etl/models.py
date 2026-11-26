from collections.abc import Mapping
from datetime import datetime
from enum import StrEnum
import string
from typing import Annotated
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, EmailStr, Field, PositiveInt
from pydantic.types import UuidVersion
from pytest import fail


class RunStatus(StrEnum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    PARTLY = "succeeded_with_errors"
    FAILED = "failed"


class Run(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: Annotated[UUID, UuidVersion(4)] = Field(default_factory=uuid4)
    started_at: datetime
    finished_at: datetime
    status: RunStatus = Field(default=RunStatus.RUNNING)
    rows_in: int
    rows_out: int
    error_message: str | None = Field(default=None)


class Row(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: Annotated[UUID, UuidVersion(4)] = Field(default_factory=uuid4)
    name: str = Field(min_length=1)
    email: EmailStr = Field(min_length=1)
    amount: PositiveInt
    source_id: int
    created_at: datetime = Field(default_factory=datetime.now)


class RowCert(BaseModel):
    model_config = ConfigDict(frozen=True)

    row_id: int
    error_message: str | None
    row_content: Row | RawRow | None


class Args(BaseModel):
    model_config = ConfigDict(frozen=True)

    db: str | None = None
    file: str
    test: bool = False
    transform: bool = False


RawRow = Mapping[str, str | None]
NormalizedRow = dict[str, str | int | UUID | datetime | None]
