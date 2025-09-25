from __future__ import annotations

import base64
from typing import Final

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _derive_key(key_b64: str) -> bytes:
    try:
        return base64.b64decode(key_b64)
    except Exception as exc:  # noqa: BLE001
        raise ValueError("Invalid base64 key for PHI encryption") from exc


def encrypt_text(plaintext: str, key_b64: str) -> str:
    key: Final = _derive_key(key_b64)
    aes = AESGCM(key)
    nonce = AESGCM.generate_key(bit_length=96)[:12]
    ciphertext = aes.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("utf-8")


def decrypt_text(token_b64: str, key_b64: str) -> str:
    key: Final = _derive_key(key_b64)
    data = base64.b64decode(token_b64)
    nonce, ciphertext = data[:12], data[12:]
    aes = AESGCM(key)
    plaintext = aes.decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")

