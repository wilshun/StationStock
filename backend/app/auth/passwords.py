from pwdlib import PasswordHash


_password_hash = PasswordHash.recommended()
_dummy_password_hash = _password_hash.hash("stationstock-invalid-user-password")


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _password_hash.verify(password, password_hash)
    except (TypeError, ValueError):
        return False


def perform_dummy_password_check(password: str) -> None:
    _password_hash.verify(password, _dummy_password_hash)
