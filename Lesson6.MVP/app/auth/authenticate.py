from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from services.user_service import UserService, User
from database.database import get_session
from auth.jwt_handler import verify_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/signin")

async def authenticate(token: str = Depends(oauth2_scheme)) -> str:

    payload = verify_access_token(token)
    return payload["user"]  

async def get_current_user(email: str = Depends(authenticate), session=Depends(get_session)) -> User:

    user_service = UserService(session)
    user = user_service.get_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )
    return user

