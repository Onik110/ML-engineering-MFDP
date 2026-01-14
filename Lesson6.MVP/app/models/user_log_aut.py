from pydantic import BaseModel

class UserCreateLogin(BaseModel):
    email: str
    password: str
