"""
Encryption utilities for sensitive fields.

- Emails: AES-256-GCM encryption + HMAC blind index for querying
- OTP codes: argon2id hashing (one-way, verify-only)

Required environment variables:
    FIELD_ENCRYPTION_KEY: 32 random bytes, base64-encoded
                          Generate: python -c "import os,base64; print(base64.b64encode(os.urandom(32)).decode())"
    FIELD_HMAC_KEY:       Any long random string (≥32 chars recommended)
                          Generate: python -c "import secrets; print(secrets.token_hex(32))"
"""

import os
import hmac
import hashlib
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

from app.core.config import settings  # add this import

def _load_encryption_key() -> bytes:
    if not settings.FIELD_ENCRYPTION_KEY:
        raise RuntimeError("FIELD_ENCRYPTION_KEY is not set.")
    key = base64.b64decode(settings.FIELD_ENCRYPTION_KEY)
    if len(key) != 32:
        raise RuntimeError("FIELD_ENCRYPTION_KEY must decode to exactly 32 bytes.")
    return key

def _load_hmac_key() -> bytes:
    if not settings.FIELD_HMAC_KEY:
        raise RuntimeError("FIELD_HMAC_KEY is not set.")
    return settings.FIELD_HMAC_KEY.encode()


_ENCRYPTION_KEY: bytes = _load_encryption_key()
_HMAC_KEY: bytes = _load_hmac_key()

# argon2id hasher with sensible defaults
_ph = PasswordHasher(time_cost=2, memory_cost=65536, parallelism=2)


# ---------------------------------------------------------------------------
# Email encryption (AES-256-GCM)
# ---------------------------------------------------------------------------

def encrypt_field(plaintext: str) -> str:
    """
    Encrypt a string with AES-256-GCM.
    Returns a base64-encoded string: nonce (12 bytes) + ciphertext + tag.
    Each call produces a different ciphertext (random nonce) — not searchable.
    Use blind_index() for equality lookups.
    """
    aesgcm = AESGCM(_ENCRYPTION_KEY)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("ascii")


def decrypt_field(encrypted: str) -> str:
    """
    Decrypt an AES-256-GCM encrypted field produced by encrypt_field().
    Raises cryptography.exceptions.InvalidTag if tampered.
    """
    aesgcm = AESGCM(_ENCRYPTION_KEY)
    raw = base64.b64decode(encrypted)
    nonce, ciphertext = raw[:12], raw[12:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")


# ---------------------------------------------------------------------------
# Blind index (HMAC-SHA256) — for searching encrypted fields
# ---------------------------------------------------------------------------

def blind_index(value: str) -> str:
    """
    Compute a deterministic HMAC-SHA256 blind index for an encrypted field.
    Normalises to lowercase before hashing.

    Store this alongside the encrypted value and query by it:
        WHERE email_index = blind_index(user_input)
    """
    return hmac.new(_HMAC_KEY, value.strip().lower().encode("utf-8"), hashlib.sha256).hexdigest()


# ---------------------------------------------------------------------------
# OTP hashing (argon2id) — one-way, never decrypt
# ---------------------------------------------------------------------------

def hash_otp(code: str) -> str:
    """Hash a plain OTP code with argon2id before storing."""
    return _ph.hash(code)


def verify_otp(hashed: str, code: str) -> bool:
    """
    Verify a plain OTP code against its stored hash.
    Returns False on mismatch; never raises.
    """
    try:
        return _ph.verify(hashed, code)
    except (VerifyMismatchError, InvalidHashError):
        return False