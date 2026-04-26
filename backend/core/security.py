import secrets
import hashlib
from datetime import datetime, timedelta

def generate_session_token() -> str:
    """Generate a secure random session token."""
    return secrets.token_hex(32)

def generate_hash(data: str) -> str:
    """Generate a SHA-256 hash."""
    return hashlib.sha256(data.encode()).hexdigest()

def is_token_expired(created_at: datetime, expiry_hours: int = 24) -> bool:
    """Check if a session token has expired."""
    return datetime.utcnow() > created_at + timedelta(hours=expiry_hours)
