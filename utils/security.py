from jose import jwt, JWTError
from sqlalchemy.orm import Session
from database.models import Usuario
from datetime import datetime, timedelta



SECRET_KEY="1234567890"
TOKEN_SECONDS_EXP=3600

def create_token(data: dict):
    data_token = data.copy()
    data_token["exp"] = datetime.utcnow() + timedelta(seconds=TOKEN_SECONDS_EXP)
    token_jwt = jwt.encode(data_token, key=SECRET_KEY, algorithm="HS256")
    return token_jwt

def decode_token(token:str):
    return jwt.decode(token, key=SECRET_KEY, algorithms=["HS256"])

def get_user(username: str, db: Session):
    return db.query(Usuario).filter(Usuario.email == username).first()

def authenticate_user(stored_password: str, input_password: str):
    return stored_password == input_password