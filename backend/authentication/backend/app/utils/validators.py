import re
from email_validator import EmailNotValidError, validate_email


def normalize_email(email: str) -> str:
    return validate_email(email, check_deliverability=False)["email"].lower()


def validate_password(password: str) -> bool:
    return bool(password) and len(password) >= 8 and bool(re.search(r"[A-Za-z]", password)) and bool(re.search(r"\d", password))


def is_valid_email(email: str) -> bool:
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False
