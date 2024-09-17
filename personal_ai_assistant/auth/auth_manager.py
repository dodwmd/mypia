from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from personal_ai_assistant.models.user import User
from personal_ai_assistant.utils.encryption import EncryptionManager
from personal_ai_assistant.database.db_manager import DatabaseManager
from personal_ai_assistant.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/token")


class AuthManager:
    def __init__(self, db_manager: DatabaseManager, encryption_manager: EncryptionManager):
        self.db_manager = db_manager
        self.encryption_manager = encryption_manager

    def authenticate_user(self, username: str, password: str):
        db = next(self.db_manager.get_db())
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return False
        if not self.encryption_manager.verify_password(password, user.hashed_password):
            return False
        return user

    def create_user(self, username: str, email: str, password: str):
        db = next(self.db_manager.get_db())
        hashed_password = self.encryption_manager.hash_password(password)
        user = User(username=username, email=email, hashed_password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def create_access_token(self, data: dict, expires_delta: timedelta = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, str(settings.secret_key), algorithm=settings.algorithm)
        return str(encoded_jwt)  # Ensure the return value is a string

    def get_current_user(self, token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        db = next(self.db_manager.get_db())
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise credentials_exception
        return user

    # Add other authentication-related methods here
