from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database.database import SessionLocal, get_db
from database.models import Usuario
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="views")

@router.get("/select-role")
async def select_role(request:Request):
    return templates.TemplateResponse("signup1.html", {"request":request})

# Ruta para mostrar el formulario de registro de pacientes (GET)
@router.get("/register-patient")
async def register_patient_form(request: Request):
    return templates.TemplateResponse("viewsU/signupU.html", {"request": request})

@router.post("/register-patient")
async def register_patient(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    email: str = Form(...),
    fecha_nacimiento: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    nuevo_usuario = Usuario(
        nombre=nombre,
        apellido=apellido,
        email=email,
        fecha_nacimiento=fecha_nacimiento,
        password=password,
        rol=0,  # Paciente
    )
    db.add(nuevo_usuario)
    db.commit()
    return RedirectResponse("/", status_code=303)

@router.get("/register-doctor")
async def register_doctor_form(request: Request):
    return templates.TemplateResponse("viewsDoc/signupDoc.html", {"request": request})


@router.post("/register-doctor")
async def register_doctor(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    email: str = Form(...),
    fecha_nacimiento: str = Form(...),
    password: str = Form(...),
    cedula_profesional: str = Form(...),
    especialidad: str = Form(...),
    db: Session = Depends(get_db),
):
    nuevo_usuario = Usuario(
        nombre=nombre,
        apellido=apellido,
        email=email,
        fecha_nacimiento=fecha_nacimiento,
        password=password,
        rol=1,  # Doctor
        cedula_profesional=cedula_profesional,
        especialidad=especialidad,
    )
    db.add(nuevo_usuario)
    db.commit()
    return RedirectResponse("/", status_code=303)

@router.post("/select-role-patient")
async def select_role_patient():
    return RedirectResponse("/register-patient", status_code=303)

@router.post("/select-role-doctor")
async def select_role_doctor():
    return RedirectResponse("/register-doctor", status_code=303)