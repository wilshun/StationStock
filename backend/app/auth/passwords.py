from pwdlib import PasswordHash
import re


_password_hash = PasswordHash.recommended()
_dummy_password_hash = _password_hash.hash("stationstock-invalid-user-password")


def validate_password_strength(password: str) -> str:
    if len(password) < 12 or not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password) or not re.search(r"\d", password):
        raise ValueError("Password must be at least 12 characters and include uppercase, lowercase, and a number")
    return password


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _password_hash.verify(password, password_hash)
    except (TypeError, ValueError):
        return False


def perform_dummy_password_check(password: str) -> None:
    _password_hash.verify(password, _dummy_password_hash)
