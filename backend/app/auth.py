from dotenv import load_dotenv
import os
from pathlib import Path
from ldap3 import Server, Connection, ALL, NTLM
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

DC_HOST = os.getenv("DC_HOST")
DC_DOMAIN = os.getenv("DC_DOMAIN")
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGO = "HS256"
JWT_EXPIRE = 480

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/bearcat-brain/api/auth/login")

class LoginRequest(BaseModel):
    username: str
    password: str

# check username and password against dc
def ldap_authentication(username: str, password: str) -> bool:
    try:
        server = Server(DC_HOST, get_info=ALL)
        user = f"{DC_DOMAIN}\\{username}"   # format username as "DOMAIN\username"
        conn = Connection(
            server,
            user=user,
            password=password,
            authentication=NTLM,
            auto_bind=True  # immediately attempts login
        )
        conn.unbind()
        return True
    except Exception as e:
        print(f"LDAP authentication failed: {e}")
        return False
    
# create jwt token after successful login
def create_jwt(username: str) -> str:
    payload = {
        "subject": username,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRE)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

# for api endpoints that require authentication
async def verify_token(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return paload["subject"]
    except JWTError:
        raise HTTPException(status_code=401, details="Cookie invalid or expiered")


