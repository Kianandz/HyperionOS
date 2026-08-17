import pamela

def verify_linux_user(username: str, password: str) -> bool:

    try:

        pamela.authenticate(username, password, service='passwd')

        return True
    
    except pamela.PAMError as e:

        print(f"[PAM Error] {e}")

        return False
    