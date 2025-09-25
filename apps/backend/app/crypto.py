from __future__ import annotations

import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os


def _get_key() -> bytes:
    raw = os.getenv("FIELD_ENCRYPTION_KEY")
    if not raw:
        # 32 bytes for AES-256; base64 encoded in env for portability
        raise RuntimeError("FIELD_ENCRYPTION_KEY is not set")
    try:
        return base64.b64decode(raw)
    except Exception as exc:
        raise RuntimeError("Invalid FIELD_ENCRYPTION_KEY") from exc


def encrypt_value(plaintext: str) -> bytes:
    key = _get_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return nonce + ciphertext


def decrypt_value(blob: bytes) -> str:
    key = _get_key()
    aesgcm = AESGCM(key)
    nonce, ciphertext = blob[:12], blob[12:]
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")

