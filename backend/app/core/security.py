"""
Security utilities - Password hashing and JWT tokens
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import hashlib
from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    try:
        result = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        return result
    except Exception as e:
        raise


def get_password_hash(password: str) -> str:
    """Hash a password"""
    # Generate salt and hash password
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_id_hash(id_number: str) -> bytes:
    """Generate a hash for ID number lookup (for multi-unit ownership linking)
    
    Uses SHA-256 with a salt to ensure privacy while allowing lookups.
    Normalizes the input (removes spaces, converts to uppercase) before hashing.
    """
    if not id_number:
        return None
    
    # Normalize: remove spaces, dashes, convert to uppercase
    normalized = id_number.replace(' ', '').replace('-', '').upper()
    
    # Use a salt from settings (or default) to prevent rainbow table attacks
    salt = getattr(settings, 'ID_HASH_SALT', 'tama38_owner_id_salt_v1').encode('utf-8')
    
    # Generate hash
    hash_obj = hashlib.sha256()
    hash_obj.update(salt)
    hash_obj.update(normalized.encode('utf-8'))
    
    return hash_obj.digest()


def generate_phone_hash(phone: str) -> bytes:
    """Generate a hash for phone number lookup (for multi-unit ownership linking)
    
    Uses SHA-256 with a salt to ensure privacy while allowing lookups.
    Normalizes the input (removes spaces, dashes, plus signs) before hashing.
    """
    if not phone:
        return None
    
    # Normalize: remove spaces, dashes, plus signs
    normalized = phone.replace(' ', '').replace('-', '').replace('+', '').replace('(', '').replace(')', '')
    
    # Use a salt from settings (or default) to prevent rainbow table attacks
    salt = getattr(settings, 'PHONE_HASH_SALT', 'tama38_owner_phone_salt_v1').encode('utf-8')
    
    # Generate hash
    hash_obj = hashlib.sha256()
    hash_obj.update(salt)
    hash_obj.update(normalized.encode('utf-8'))
    
    return hash_obj.digest()

