from fastapi import APIRouter, HTTPException, status, Depends
from database.database import get_session
from models.user_log_aut import UserCreateLogin
from services.user_service import UserService
from fastapi.security import OAuth2PasswordRequestForm
from auth.authenticate import authenticate
from models.user import User
from typing import Dict, List
import logging
from auth.jwt_handler import create_access_token


logger = logging.getLogger(__name__)

user_route = APIRouter()


@user_route.post(
    '/signup',
    response_model=Dict[str, str],
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description='Registration a new user with email and password'
)
async def signup(data: UserCreateLogin, session=Depends(get_session)) -> Dict[str, str]:
    try:
        user_service = UserService(session)
        user_service.create_user(data.email, data.password)
        logger.info(f"New user registered: {data.email}")
        return {"message": "User successfully registered"}

    except ValueError as e:
        error_msg = str(e)
        if "already exists" in error_msg:
            logger.warning(f"Signup attempt with existing email: {data.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        else:
            logger.warning(f"Validation error: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input: {error_msg}"
            )
    
    except Exception as e:
        logger.error(f"Error during signup: {str(e)}") 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )
    
@user_route.post('/signin')
async def signin(data: OAuth2PasswordRequestForm = Depends(), session=Depends(get_session)) -> Dict[str, str]:

    user_service = UserService(session)
    user = user_service.get_by_email(data.username)
    if not user:
        raise HTTPException(status_code=404, detail="User doesn't exist")
    
    user_service.password = user.password
    
    if not user_service.check_password(data.password):
        raise HTTPException(status_code=403, detail="Wrong password")

    access_token = create_access_token(user.email)
    
    return {"message": "User signed in successfully",
        "access_token": access_token     
    }


@user_route.get(
    "/all-users",
    response_model=List[User],
    status_code=status.HTTP_200_OK,
    summary="Get all users",
    description="Returns a list of all registered users"
)
def get_all_users(session=Depends(get_session)):
    user_service = UserService(session)
    try:
        users = user_service.get_all_users()
        logger.info(f"Retrieved {len(users)} users")
        return users
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )

    
@user_route.get("/me")
async def get_current_user(email: str = Depends(authenticate), session=Depends(get_session)):
    user_service = UserService(session)
    user = user_service.get_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "email": user.email}
