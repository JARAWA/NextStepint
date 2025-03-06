import json
from pathlib import Path
from typing import Optional, Dict
import os
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    # Generate a secure random key if not provided
    import secrets
    SECRET_KEY = secrets.token_hex(32)
    print(f"Warning: Using generated SECRET_KEY: {SECRET_KEY}")
    print("Please set JWT_SECRET_KEY environment variable for production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class User(BaseModel):
    email: str
    full_name: str
    hashed_password: str

class UserStorage:
    def __init__(self):
        self.file_path = Path(__file__).parent.parent / 'data' / 'users.json'
        self.users: Dict[str, dict] = self._load_users()

    def _load_users(self) -> Dict[str, dict]:
        """Load users from JSON file."""
        try:
            if self.file_path.exists():
                with open(self.file_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading users: {str(e)}")
            return {}

    def _save_users(self) -> bool:
        """Save users to JSON file."""
        try:
            self.file_path.parent.mkdir(exist_ok=True)
            with open(self.file_path, 'w') as f:
                json.dump(self.users, f)
            return True
        except Exception as e:
            logger.error(f"Error saving users: {str(e)}")
            return False

    def get_user(self, email: str) -> Optional[User]:
        """Get user by email."""
        user_data = self.users.get(email)
        if user_data:
            return User(**user_data)
        return None

    def add_user(self, user: User) -> bool:
        """Add new user."""
        try:
            self.users[user.email] = user.dict()
            return self._save_users()
        except Exception as e:
            logger.error(f"Error adding user: {str(e)}")
            return False

    def update_user(self, user: User) -> bool:
        """Update existing user."""
        try:
            if user.email not in self.users:
                return False
            self.users[user.email] = user.dict()
            return self._save_users()
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return False

    def delete_user(self, email: str) -> bool:
        """Delete user."""
        try:
            if email not in self.users:
                return False
            del self.users[email]
            return self._save_users()
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return False

# Initialize user storage
user_storage = UserStorage()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.JWTError:
        logger.warning("Invalid token")
        return None

async def register_user(email: str, password: str, full_name: str) -> bool:
    try:
        # Check if user already exists
        if user_storage.get_user(email):
            return False
        
        # Create new user
        hashed_password = get_password_hash(password)
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password
        )
        
        # Save user
        return user_storage.add_user(user)
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return False

async def authenticate_user(email: str, password: str) -> Optional[User]:
    try:
        user = user_storage.get_user(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    except Exception as e:
        logger.error(f"Error authenticating user: {str(e)}")
        return None
