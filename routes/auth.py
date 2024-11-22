from typing import Annotated
from fastapi import APIRouter, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from utils.security import authenticate_user, create_token, get_user, TOKEN_SECONDS_EXP
from database.database import get_db, SessionLocal, engine, Base
from database.models import Usuario

router=APIRouter()

# Ruta para iniciar sesión
@router.post("/users/login")
def login(username: Annotated[str, Form()], password: Annotated[str, Form()], db: Session = Depends(get_db)):
    user_data = get_user(username, db)
    if user_data is None:
        raise HTTPException(
            status_code=401,
            detail="Usuario no encontrado o no autorizado"
        )
    if not authenticate_user(user_data.password, password):
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas"
        )
    token = create_token({"username": user_data.email})
    return RedirectResponse("/users/dashboard", status_code=302, headers={"set-cookie": f"access_token={token}; Max-Age={TOKEN_SECONDS_EXP}"})

# Ruta para cerrar sesión
@router.post("/users/logout")
def logout():
    return RedirectResponse("/", status_code=302, headers={
        "set-cookie": "access_token=; Max-Age=0"
    })