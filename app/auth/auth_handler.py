import time
from typing import Dict, Optional
import jwt
from app.config.settings import environment_secrets


def token_response(access_token: str, refresh_token: str):
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


def sign_jwt(user_id: str, expires: Optional[int] = None, token_type: str = "access") -> str:
    payload = {
        "user_id": str(user_id),
        "type": token_type  # incluir tipo no token
    }

    if expires is not None:
        payload["expires"] = time.time() + expires

    token = jwt.encode(
        payload,
        environment_secrets['JWT_SECRET'],
        algorithm=environment_secrets['JWT_ALGORITHM']
    )
    return token



def decode_jwt(token: str) -> Optional[dict]:
    try:
        decoded_token = jwt.decode(token, environment_secrets['JWT_SECRET'], algorithms=[environment_secrets['JWT_ALGORITHM']])
        if "expires" in decoded_token and decoded_token["expires"] < time.time():
            return None
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None
    except jwt.DecodeError:
        return None
