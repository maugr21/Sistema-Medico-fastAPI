from datetime import datetime
from fastapi import APIRouter, Form, Request, Cookie, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database.models import Usuario, CitaMedica, RecMedicaPaciente
from utils.security import decode_token, get_user
from database.database import get_db
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates=Jinja2Templates(directory="views")

@router.get("/users/dashboard-doc", response_class=RedirectResponse)
def dashboard_doc(request: Request, access_token: str | None = Cookie(None), db: Session = Depends(get_db)):
    if not access_token:
        return RedirectResponse("/", status_code=302)
    
    try:
        user_data = decode_token(access_token)
        user = get_user(user_data["username"], db)
        if not user or user.rol != 1: 
            return RedirectResponse("/", status_code=302)
        
        citas=(
            db.query(CitaMedica)
            .filter(CitaMedica.id_medico == user.id_usuario).all()
        )
        return templates.TemplateResponse("viewsDoc/dashboard.html", {"request": request, "citas":citas})
    except Exception as e:
        print(f"{e}")
        return RedirectResponse("/", status_code=302)


@router.get("/users/crear-receta/{id_cita}", response_class=HTMLResponse)
def crear_receta_form(id_cita:int, request:Request, access_token:str | None=Cookie(None),query_access_token:str | None = None, db:Session = Depends(get_db)):
    token= access_token or query_access_token
    if not access_token:
        return RedirectResponse("/", status_code=302)
    
    try: 
        user_data=decode_token(access_token)
        user=get_user(user_data["username"],db)
        
        if not user or user.rol !=1:
            return RedirectResponse("/", status_code=302)
        
        cita=db.query(CitaMedica).filter(CitaMedica.id_cita==id_cita).first()
        if not cita:
            return RedirectResponse("/users/dashboard-doc", status_code=302)
        
        return templates.TemplateResponse("viewsDoc/crear_receta.html", {"request":request, "cita":cita})
    except Exception as e:
        print(f"Error al cargar el formulario de la receta: {e}")
        return RedirectResponse("/", status_code=302)
    
    
@router.post("/users/crear-receta/{id_cita}", response_class=RedirectResponse)
def crear_receta(
    id_cita:int,
    anotaciones_receta_paciente:str=Form(...),
    access_token:str | None = Cookie(None),
    db: Session = Depends(get_db)
):
    try:
        if not access_token:
            return RedirectResponse("/", status_code=302)
        
        user_data=decode_token(access_token)
        user=get_user(user_data["username"],db)
        
        if not user or user.rol != 1:
            return RedirectResponse("/", status_code=302)
        
        cita=db.query(CitaMedica).filter(CitaMedica.id_cita==id_cita).first()
        if not cita:
            return RedirectResponse("/users/dashboard-doc", status_code=302)
        
        nueva_receta=RecMedicaPaciente(
            id_usuario=cita.id_usuario,
            id_medico=user.id_usuario,
            anotaciones_receta_paciente=anotaciones_receta_paciente,
            fecha_cita=cita.fecha_cita
        )
        db.add(nueva_receta)
        db.commit()
        
        return RedirectResponse("/users/dashboard-doc", status_code=302)
    except Exception as e:
        print(f"Error al crear la receta: {e}")
        return RedirectResponse("/", status_code=302)