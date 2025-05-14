from datetime import datetime,timedelta
import random
import string
from datetime import datetime, timedelta
from fastapi import Request
import base64


def future_date(days: int) -> datetime:
    return datetime.now() + timedelta(days=days)


def generate_token(length=5):
    characters = string.ascii_letters + string.digits
    token = ''.join(random.choices(characters, k=length))
    return token


def datetime_now(fuso=False):
    agora = datetime.now()
    if fuso:
        tres_horas_atras = agora - timedelta(hours=3)
        return tres_horas_atras
    else:
        return agora



def encode_base64(value: str) -> str:
    encoded_bytes = base64.b64encode(value.encode('utf-8'))
    encoded_str = encoded_bytes.decode('utf-8')
    return encoded_str


def decode_base64(encoded_str: str) -> str:
    decoded_bytes = base64.b64decode(encoded_str.encode('utf-8'))
    return decoded_bytes.decode('utf-8')