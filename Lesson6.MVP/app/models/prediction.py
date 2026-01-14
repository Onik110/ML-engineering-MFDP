from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class MLPrediction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    model_name: str
    prediction_result: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)

    user: Optional["User"] = Relationship(back_populates="predictions")