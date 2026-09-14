import pamela
from .logger import logger


def verify_linux_user(username: str, password: str) -> bool:
    try:
        pamela.authenticate(username, password, service="passwd")
        return True
    except pamela.PAMError as e:
        logger.warning(f"Failed login attempt for user '{username}': {e}")
        return False
