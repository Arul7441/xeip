from __future__ import annotations

import base64
import hashlib
from os import getenv

from cryptography.fernet import Fernet


def _fernet() -> Fernet:
    raw = getenv("XEIP_ENCRYPTION_KEY", "xeip-local-development-key")
    key = base64.urlsafe_b64encode(hashlib.sha256(raw.encode("utf-8")).digest())
    return Fernet(key)


def encrypt_text(value: str) -> str:
    return _fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_text(value: str) -> str:
    return _fernet().decrypt(value.encode("utf-8")).decode("utf-8")
