"""
Credential Encryption Service
==============================
Uses Fernet (AES-128-CBC with HMAC-SHA256) from the `cryptography` library.
The encryption key is loaded from the ENCRYPTION_KEY environment variable.
A new Fernet key can be generated with: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
"""
import os
import json
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

_ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")


def _get_fernet() -> Fernet:
    """Return a configured Fernet instance. Raises if key is missing/invalid."""
    if not _ENCRYPTION_KEY:
        raise RuntimeError("ENCRYPTION_KEY environment variable is not set.")
    key = _ENCRYPTION_KEY.encode() if isinstance(_ENCRYPTION_KEY, str) else _ENCRYPTION_KEY
    return Fernet(key)


def encrypt_credentials(credentials: dict) -> str:
    """Encrypt a credentials dict to a base64-encoded string."""
    f = _get_fernet()
    payload = json.dumps(credentials).encode()
    return f.encrypt(payload).decode()


def decrypt_credentials(encrypted: str) -> dict:
    """Decrypt a base64-encoded credentials string back to a dict."""
    f = _get_fernet()
    decrypted = f.decrypt(encrypted.encode())
    return json.loads(decrypted.decode())


def credentials_hash(credentials: dict) -> str:
    """Return a stable hash for audit logging (never stores actual secret values)."""
    import hashlib
    payload = json.dumps(sorted(credentials.keys())).encode()
    return hashlib.sha256(payload).hexdigest()[:16]
