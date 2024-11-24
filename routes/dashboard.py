from datetime import datetime
from fastapi import APIRouter, Form, Request, Cookie, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.models import Usuario, CitaMedica
from utils.security import decode_token, get_user
from database.database import get_db

router = APIRouter()

templates = Jinja2Templates(directory="views")
@router.get("/users/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, access_token: str | None = Cookie(None), db: Session = Depends(get_db)):
    if not access_token:
        return RedirectResponse("/", status_code=302)
    
    try:
        user_data = decode_token(access_token)
        user = get_user(user_data["username"], db)
        if not user:
            return RedirectResponse("/", status_code=302)
        
        if user.rol == 0:
            return RedirectResponse("/users/dashboard-user", status_code=302)
        elif user.rol == 1:
            return RedirectResponse("/users/dashboard-doc", status_code=302)
    except Exception:
        return RedirectResponse("/", status_code=302)


@router.get("/users/dashboard-user", response_class=RedirectResponse)
def dashboard_user(request: Request, access_token: str | None = Cookie(None), db: Session = Depends(get_db)):
    if not access_token:
        return RedirectResponse("/", status_code=302)
    
    try:
        user_data = decode_token(access_token)
        user = get_user(user_data["username"], db)
        if not user or user.rol != 0:  
            return RedirectResponse("/", status_code=302)
        doctors = db.query(Usuario).filter(Usuario.rol==1).all()
        return templates.TemplateResponse("viewsU/dashboard.html", {"request": request, "users":doctors})
    except Exception:
        return RedirectResponse("/", status_code=302)
    
@router.get("/users/details/{id_usuario}", response_class=HTMLResponse)
def user_details(id_usuario: int, request: Request, access_token: str | None = Cookie(None), db: Session = Depends(get_db)):
    print("Access Token in Cookie:", access_token)
    if not access_token:
        return RedirectResponse("/", status_code=302)
    try:
        user_data = decode_token(access_token) 
        print("Decoded Token Data: ", user_data)
        user = get_user(user_data["username"], db)

        if not user or user.rol != 0:
            return RedirectResponse("/", status_code=302)

        user_details = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
        if not user_details:
            return RedirectResponse("/users/dashboard-user", status_code=302)

        return templates.TemplateResponse("viewsU/user_details.html", {"request": request, "user": user_details})
    except Exception as e:
           print(f"Token Decode Error: {e}")
           return RedirectResponse("/", status_code=302)  
       
       
@router.get("/users/agendarCita/{id_usuario}", response_class=HTMLResponse)
def agendarCitaForm(id_usuario: int, request: Request, access_token: str | None = Cookie(None), db: Session = Depends(get_db)):
    if not access_token:
        return RedirectResponse("/",status_code=302)
    
    try:
        user_data=decode_token(access_token)
        user= get_user(user_data["username"], db)
        
        if not user:
            return RedirectResponse("/", status_code=302)

        medicos= db.query(Usuario).filter(Usuario.rol == 1).all()
        
        return templates.TemplateResponse("viewsU/AgendarCita.html",{"request": request, "id_usuario":id_usuario, "medicos":medicos})
    except Exception as e: 
        print(f"Error: {e}")
        return RedirectResponse("/", status_code=302)
    

@router.post("/users/agendarCita/{id_usuario}", response_class=RedirectResponse)
def agendarCita(
    id_usuario: int,
    id_medico: int = Form(...),
    fecha_cita: str = Form(...),
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):
    try:
        if not access_token:
            return RedirectResponse("/", status_code=302)

        user_data = decode_token(access_token) 
        user = get_user(user_data["username"], db) 

        if not user or user.rol != 0:  
            return RedirectResponse("/", status_code=302)
        
        nueva_cita = CitaMedica(
            id_usuario=user.id_usuario, 
            id_medico=id_medico, 
            fecha_cita=datetime.strptime(fecha_cita, "%Y-%m-%dT%H:%M"),
            confirm_cita=False
        )
        db.add(nueva_cita)
        db.commit()
        return RedirectResponse(f"/users/details/{id_usuario}", status_code=302)
    except Exception as e:
        print(f"Error al agendar cita: {e}")
        return RedirectResponse("/", status_code=302)
    
@router.get("/users/misCitas", response_class=HTMLResponse)
def mis_citas(
    request: Request,
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        return RedirectResponse("/", status_code=302)

    try:
        user_data = decode_token(access_token)
        user = get_user(user_data["username"], db)
        if not user or user.rol != 0: 
            return RedirectResponse("/", status_code=302)
        citas = (
            db.query(CitaMedica)
            .filter(CitaMedica.id_usuario == user.id_usuario)
            .all()
        )

        return templates.TemplateResponse(
            "viewsU/citas.html", {"request": request, "user": user, "citas": citas}
        )
    except Exception as e:
        print(f"Error al obtener citas: {e}")
        return RedirectResponse("/", status_code=302)
    
    
@router.post("/users/eliminarCita/{id_cita}", response_class=RedirectResponse)
def eliminar_cita(
    id_cita: int,
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):
    try:
        if not access_token:
            return RedirectResponse("/", status_code=302)

        user_data = decode_token(access_token)
        user = get_user(user_data["username"], db)

        if not user or user.rol != 0:
            return RedirectResponse("/", status_code=302)

        cita = db.query(CitaMedica).filter(CitaMedica.id_cita == id_cita, CitaMedica.id_usuario == user.id_usuario).first()
        if cita:
            db.delete(cita)
            db.commit()

        return RedirectResponse("/users/misCitas", status_code=302)
    except Exception as e:
        print(f"Error al eliminar cita: {e}")
        return RedirectResponse("/users/misCitas", status_code=302)

@router.get("/users/editarCita/{id_cita}", response_class=HTMLResponse)
def editar_cita_form(
    id_cita: int,
    request: Request,
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        return RedirectResponse("/", status_code=302)

    try:
        user_data = decode_token(access_token)
        user = get_user(user_data["username"], db)

        if not user or user.rol != 0:
            return RedirectResponse("/", status_code=302)

        cita = db.query(CitaMedica).filter(CitaMedica.id_cita == id_cita, CitaMedica.id_usuario == user.id_usuario).first()
        if not cita:
            return RedirectResponse("/users/misCitas", status_code=302)

        medicos = db.query(Usuario).filter(Usuario.rol == 1).all()
        return templates.TemplateResponse("viewsU/editarCita.html", {"request": request, "cita": cita, "medicos": medicos})
    except Exception as e:
        print(f"Error al obtener cita: {e}")
        return RedirectResponse("/users/misCitas", status_code=302)

@router.post("/users/editarCita/{id_cita}", response_class=RedirectResponse)
def editar_cita(
    id_cita: int,
    id_medico: int = Form(...),
    fecha_cita: str = Form(...),
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):
    try:
        if not access_token:
            return RedirectResponse("/", status_code=302)

        user_data = decode_token(access_token)
        user = get_user(user_data["username"], db)

        if not user or user.rol != 0:
            return RedirectResponse("/", status_code=302)

        cita = db.query(CitaMedica).filter(CitaMedica.id_cita == id_cita, CitaMedica.id_usuario == user.id_usuario).first()
        if not cita:
            return RedirectResponse("/users/misCitas", status_code=302)

        cita.id_medico = id_medico
        cita.fecha_cita = datetime.strptime(fecha_cita, "%Y-%m-%dT%H:%M")
        db.commit()

        return RedirectResponse("/users/misCitas", status_code=302)
    except Exception as e:
        print(f"Error al editar cita: {e}")
        return RedirectResponse("/users/misCitas", status_code=302)

    


