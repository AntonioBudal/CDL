from datetime import datetime

from app.schemas.common import OutputModel


class UserRead(OutputModel):
    id: str
    username: str
    display_name: str
    status: str
    created_at: datetime
