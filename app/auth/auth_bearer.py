from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.auth_handler import decode_jwt

class JWTBearer(HTTPBearer):
    def __init__(self, token_types: list[str] = ["access"], cookie_name: str = "a_mgm", auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        self.token_types = token_types
        self.cookie_name = cookie_name

    async def __call__(self, request: Request):
        token = None

        # 1. Primeiro tenta pegar do header Authorization
        try:
            credentials: HTTPAuthorizationCredentials = await super().__call__(request)
            if credentials and credentials.scheme == "Bearer":
                token = credentials.credentials
        except:
            pass  # ignora erro aqui e tenta pegar do cookie

        # 2. Se não houver token no header, tenta buscar no cookie
        if not token:
            token = request.cookies.get(self.cookie_name)

        # 3. Se ainda assim não tiver token, erro
        if not token:
            raise HTTPException(status_code=403, detail="Token not found in header or cookies")

        # 4. Validação do JWT
        if not self.verify_jwt(token):
            raise HTTPException(status_code=403, detail="Invalid or expired token")

        return token

    def verify_jwt(self, jwtoken: str) -> bool:
        try:
            payload = decode_jwt(jwtoken)
            return payload and payload.get("type") in self.token_types
        except:
            return False
