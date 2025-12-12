from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from typing import Optional
from app.core.config import settings

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

BCRYPT_MAX_BYTES = 72

def _truncate_password_for_bcrypt(password: str) -> str:
    """
    Ensure bcrypt's 72-byte limit isn't exceeded.
    This truncates the UTF-8 byte string to 72 bytes and decodes
    back to str using 'ignore' for partial multibyte characters.
    """
    if password is None:
        return ""
    b = password.encode("utf-8")
    if len(b) <= BCRYPT_MAX_BYTES:
        return password
    # truncate bytes then decode ignoring partial multi-byte char
    truncated = b[:BCRYPT_MAX_BYTES].decode("utf-8", errors="ignore")
    return truncated

def hash_password(password: str) -> str:
    safe_password = _truncate_password_for_bcrypt(password)
    return pwd_ctx.hash(safe_password)

def verify_password(plain: str, hashed: str) -> bool:
    # For verification we must apply the same truncation rule
    # because hashed passwords were created using the truncated version.
    safe_plain = _truncate_password_for_bcrypt(plain)
    return pwd_ctx.verify(safe_plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=(expires_delta or settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

def decode_token(token: str) -> dict:
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    return payload
