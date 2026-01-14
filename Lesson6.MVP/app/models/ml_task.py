from enum import Enum
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from pydantic import BaseModel

class TaskStatus(str, Enum):
    PENDING = "в ожидании"
    PROCESSING = "обработка"
    DONE = "выполнено"
    FAILED = "ошибка"

class MLTask(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    model_name: str
    input_data: str
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result_id: int | None = None

    user: Optional["User"] = Relationship(back_populates="ml_tasks")

 