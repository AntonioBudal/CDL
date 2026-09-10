from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

SQLITE_MAX_INTEGER = 2**63 - 1
RecordId = Annotated[int, Field(gt=0, le=SQLITE_MAX_INTEGER)]
Position = Annotated[int, Field(ge=0, le=SQLITE_MAX_INTEGER)]
NonBlankText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class InputModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class OutputModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
