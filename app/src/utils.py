from datetime import datetime,timedelta
import random
import string
from datetime import datetime, timedelta
from fastapi import Request
import base64
import urllib.parse
import binascii

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
    try:
        # Primeiro, tentar o unquote (não afeta strings já decodificadas)
        decoded_url = urllib.parse.unquote(encoded_str)
        
        # Corrigir padding do base64 se necessário
        missing_padding = len(decoded_url) % 4
        if missing_padding:
            decoded_url += '=' * (4 - missing_padding)

        # Tentar decodificar Base64
        decoded_bytes = base64.b64decode(decoded_url)
        return decoded_bytes.decode('utf-8').strip('"')

    except (binascii.Error, UnicodeDecodeError) as e:
        return f"Erro ao decodificar: {e}"