from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import timedelta
import logging

from personal_ai_assistant.auth.auth_manager import AuthManager
from personal_ai_assistant.config.config import settings
from personal_ai_assistant.api.dependencies import get_auth_manager
from personal_ai_assistant.models.user import User  # Add this import

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
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_manager: AuthManager = Depends(get_auth_manager)
):
    user = auth_manager.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth_manager.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=str(access_token), token_type="bearer")

@router.get("/user/info", response_model=UserResponse)
async def get_user_info(
    auth_manager: AuthManager = Depends(get_auth_manager),
    token: str = Depends(oauth2_scheme)
):
    current_user = auth_manager.get_current_user(token)
    return UserResponse(username=current_user.username, email=current_user.email)
