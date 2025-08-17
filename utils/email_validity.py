import re
EMAIL_REGEX = r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Za-z]{2,})+"

def is_valid_email(email: str) -> bool:
    return re.fullmatch(EMAIL_REGEX, email) is not None
