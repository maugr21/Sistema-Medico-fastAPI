from fastapi import FastAPI, Request, Form, HTTPException, Cookie
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Annotated
from jose import jwt, JWTError
from datetime import datetime, timedelta

SECRET_KEY ="1234567890"
TOKEN_SECONDS_EXP=60

app = FastAPI()

jinja2_template = Jinja2Templates(directory="views")

db_users={
    "Mau":{
        "id":0,
        "username":"Mau",
        "password":"1234#Hash"
    },
    "Rodrigo":{
        "id":1,
        "username":"Rodrigo",
        "password":"12345#Hash"
    }
}

def get_user(username:str, db:list):
    if username in db:
        return db[username]
    
def authenticate_user(password:str, password_plane:str):
    password_clean = password.split("#")[0]
    if password_plane == password_clean:
        return True
    return False
    
def create_token(data:list):
    data_token=data.copy()
    data_token["exp"]=datetime.utcnow()+timedelta(seconds=TOKEN_SECONDS_EXP)
    token_jwt=jwt.encode(data_token, key=SECRET_KEY, algorithm="HS256")
    return token_jwt
    
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return jinja2_template.TemplateResponse("index.html", {"request": request})

@app.get("/users/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, access_token: Annotated[str | None, Cookie()]=None):
    if access_token is None:
        return RedirectResponse("/", status_code=302)
    try:
        data_user=jwt.decode(access_token, key = SECRET_KEY, algorithms=["HS256"])
        if get_user(data_user["username"],db_users) is None:
            return RedirectResponse("/", status_code=302)
        return jinja2_template.TemplateResponse("dashboard.html", {"request":request})
    except JWTError:
        return RedirectResponse("/", status_code=302)
    return jinja2_template.TemplateResponse("dashboard.html", {"request":request})

@app.post("/users/login")
def login(username:Annotated[str, Form()], password:Annotated[str, Form()]):
    user_data = get_user(username, db_users)
    if user_data is None:
        raise HTTPException(
            status_code=401,
            detail="No Authorization"
        )
    if not authenticate_user(user_data["password"], password):
        raise HTTPException(
            status_code=401,
            detail="Somtehing Failed"
            )
    token = create_token({"username":user_data["username"]})
    return RedirectResponse("/users/dashboard",
                            status_code=302,
                            headers={"set-cookie":f"access_token={token}; Max-Age={TOKEN_SECONDS_EXP}"})
    
@app.post("/users/logout")
def logout():
    return RedirectResponse("/", status_code=302, headers={
        "set-cookie":"access_token=; Max-Age=0"
    })