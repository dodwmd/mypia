from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, ValidationError
from datetime import timedelta
import logging

from personal_ai_assistant.auth.auth_manager import AuthManager
from personal_ai_assistant.config.config import settings
from personal_ai_assistant.api.dependencies import get_auth_manager
from personal_ai_assistant.models.user import User

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    username: str
    email: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    auth_manager: AuthManager = Depends(get_auth_manager)
):
    try:
        created_user = auth_manager.create_user(user.username, user.email, user.password)
        if not created_user:
            logger.warning(f"User creation failed for username: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists",
            )
        logger.info(f"User created successfully: {user.username}")
        return {"message": "User created successfully"}
    except Exception as e:
        logger.error(f"Error during user registration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/token", response_model=Token)
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_manager: AuthManager = Depends(get_auth_manager)
):
    try:
        user = auth_manager.authenticate_user(form_data.username, form_data.password)
        if not user:
            logger.warning(f"Failed login attempt for username: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = auth_manager.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        # Set the access token in an HTTP-only cookie
        response.set_cookie(
            key="access_token", 
            value=f"Bearer {access_token}", 
            httponly=True, 
            max_age=settings.access_token_expire_minutes * 60,
            samesite="lax",
            secure=not settings.debug  # Set to True in production
        )
        
        logger.info(f"Successful login for user: {user.username}")
        return Token(access_token=access_token, token_type="bearer")
    except ValidationError as ve:
        logger.error(f"Validation error during login: {str(ve)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}

@router.get("/user/info", response_model=UserResponse)
async def get_user_info(
    token: str = Depends(oauth2_scheme),
    auth_manager: AuthManager = Depends(get_auth_manager)
):
    try:
        current_user = auth_manager.get_current_user(token)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return UserResponse(username=current_user.username, email=current_user.email)
    except Exception as e:
        logger.error(f"Error in get_user_info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
