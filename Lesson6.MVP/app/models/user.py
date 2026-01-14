from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, min_length=5, max_length=255)
    password: str  

    predictions: List["MLPrediction"] = Relationship(back_populates="user")
    ml_tasks: List["MLTask"] = Relationship(back_populates="user")