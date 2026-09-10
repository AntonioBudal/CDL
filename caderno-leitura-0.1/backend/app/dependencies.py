from typing import Annotated

from fastapi import Depends, Path
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.common import SQLITE_MAX_INTEGER

DatabaseSession = Annotated[Session, Depends(get_session)]
Identifier = Annotated[int, Path(gt=0, le=SQLITE_MAX_INTEGER)]
