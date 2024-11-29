from datetime import datetime
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Form, Request, Cookie, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from sqlalchemy.orm import Session
from database.models import ExpClinicoPaciente, Usuario, CitaMedica, RecMedicaPaciente
from utils.security import decode_token, get_user
from database.database import get_db
from fastapi.templating import Jinja2Templates
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os



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

        #Citas y las recetas 
        citas = db.query(CitaMedica).filter(CitaMedica.id_medico == user.id_usuario).all()
        recetas = db.query(RecMedicaPaciente).filter(RecMedicaPaciente.id_medico == user.id_usuario).all()
        for cita in citas:
            cita.receta=(
                db.query(RecMedicaPaciente)
                .filter(RecMedicaPaciente.id_cita==cita.id_cita)
                .first()
            )
        return templates.TemplateResponse("viewsDoc/dashboard.html", {"request": request, "citas": citas, "recetas": recetas})
    except Exception as e:
        print(f"{e}")
        return RedirectResponse("/", status_code=302)
    
@router.get("/users/mis-citas", response_class=RedirectResponse)
def mis_citas(
    request:Request,
    access_token:str|None=Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        return RedirectResponse("/", status_code=302)
    try:
        user_data = decode_token(access_token)
        user = get_user(user_data["username"], db)
        if not user or user.rol != 1: 
            return RedirectResponse("/", status_code=302)

        #Citas y las recetas 
        citas = db.query(CitaMedica).filter(CitaMedica.id_medico == user.id_usuario).all()
        recetas = db.query(RecMedicaPaciente).filter(RecMedicaPaciente.id_medico == user.id_usuario).all()
        for cita in citas:
            cita.receta=(
                db.query(RecMedicaPaciente)
                .filter(RecMedicaPaciente.id_cita==cita.id_cita)
                .first()
            )
        return templates.TemplateResponse("viewsDoc/mis_citas.html", {"request": request, "citas": citas, "recetas": recetas})
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
    id_cita: int,
    anotaciones_receta_paciente: str = Form(...),
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        return RedirectResponse("/", status_code=302)

    try:
        user_data = decode_token(access_token)
        user = get_user(user_data["username"], db)
        if not user or user.rol != 1:
            return RedirectResponse("/", status_code=302)

        # La cita pertenece al médico
        cita = db.query(CitaMedica).filter_by(id_cita=id_cita, id_medico=user.id_usuario).first()
        if not cita:
            return RedirectResponse("/users/dashboard-doc", status_code=302)
        receta_existente = db.query(RecMedicaPaciente).filter_by(id_cita=id_cita).first()
        if receta_existente:
            return RedirectResponse("/users/dashboard-doc", status_code=302)
        nueva_receta = RecMedicaPaciente(
            id_usuario=cita.id_usuario,
            id_medico=user.id_usuario,
            id_cita=id_cita,
            anotaciones_receta_paciente=anotaciones_receta_paciente,
            fecha_cita=cita.fecha_cita
        )
        db.add(nueva_receta)
        db.commit()
        return RedirectResponse(f"/users/dashboard-doc/{nueva_receta.id_receta}", status_code=302)
    except Exception as e:
        db.rollback()
        print(f"Error al crear la receta: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

    
@router.get("/users/mis-pacientes", response_class=HTMLResponse)
def mis_pacientes(
    request:Request,
    access_token: str | None = Cookie(None),
    db: Session=Depends(get_db)
):
    if not access_token:
        return RedirectResponse("/", status_code=302)
    
    try:
        user_data=decode_token(access_token)
        user = get_user(user_data["username"], db)
        
        if not user or user.rol != 1:
            return RedirectResponse("/", status_code=302)
        
        citas=(
            db.query(CitaMedica).filter(CitaMedica.id_medico == user.id_usuario).all())
        pacientes_ids={cita.id_usuario for cita in citas}
        pacientes = db.query(Usuario).filter(Usuario.id_usuario.in_(pacientes_ids)).all()
        
        return templates.TemplateResponse(
            "viewsDoc/mis_pacientes.html",
            {"request":request, "pacientes":pacientes}
        )
    except Exception as e:
        print(f"Error al obtener pacientes:{e}")
        return RedirectResponse("/", status_code=302)
    
@router.get("/users/actualizar-receta/{id_receta}", response_class=HTMLResponse)
def formulario_actualizar_receta(
    id_receta: int,
    request: Request,
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="No autorizado")
    try:
        # Decodificar el token para obtener el id del médico
        user_data = decode_token(access_token)
        user = get_user(user_data["username"], db)
        if not user or user.rol != 1:
            raise HTTPException(status_code=403, detail="Acceso denegado")
        # Buscar la receta y verificar que pertenece al médico actual
        receta = db.query(RecMedicaPaciente).filter(
            RecMedicaPaciente.id_receta == id_receta,
            RecMedicaPaciente.id_medico == user.id_usuario
        ).first()
        if not receta:
            raise HTTPException(status_code=404, detail="Receta no encontrada o no pertenece al médico actual")
        # Renderizar el formulario de actualización
        return templates.TemplateResponse(
            "viewsDoc/actualizar_receta.html",
            {"request": request, "receta": receta}
        )
    except Exception as e:
        print(f"Error al cargar el formulario de actualización de receta: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    
@router.post("/users/actualizar-receta/{id_receta}", response_class=RedirectResponse)
def actualizar_receta(
    id_receta: int,
    anotaciones_receta_paciente: str = Form(...),
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="No autorizado")
    try:
        user_data = decode_token(access_token)
        user = get_user(user_data["username"], db)
        if not user or user.rol != 1:
            raise HTTPException(status_code=403, detail="Acceso denegado")
        receta = db.query(RecMedicaPaciente).filter_by(id_receta=id_receta, id_medico=user.id_usuario).first()
        if not receta:
            raise HTTPException(status_code=404, detail="Receta no encontrada o no pertenece al médico actual")
        receta.anotaciones_receta_paciente = anotaciones_receta_paciente
        db.commit()

        return RedirectResponse("/users/dashboard-doc", status_code=302)
    except Exception as e:
        db.rollback()
        print(f"Error al actualizar la receta: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/users/eliminar-receta/{id_receta}", response_class=JSONResponse)
@router.delete("/users/eliminar-receta/{id_receta}", response_class=JSONResponse)  # También puedes usar DELETE directamente
def eliminar_receta(
    id_receta: int,
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="No autorizado")

    try:
        user_data = decode_token(access_token)
        user = get_user(user_data["username"], db)
        if not user or user.rol != 1:
            raise HTTPException(status_code=403, detail="Acceso denegado")

        receta = db.query(RecMedicaPaciente).filter_by(id_receta=id_receta).first()
        if not receta:
            raise HTTPException(status_code=404, detail="Receta no encontrada")

        db.delete(receta)
        db.commit()

        return JSONResponse(content={"message": "Receta eliminada exitosamente"}, status_code=200)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/users/guardar-expediente/{id_usuario}", response_class=RedirectResponse)
def guardar_expediente(
    id_usuario: int,
    anotaciones_nuevas_paciente: str = Form(...),
    fecha_cita: str = Form(...),
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        return RedirectResponse("/", status_code=302)

    try:
        user_data = decode_token(access_token)
        user = get_user(user_data["username"], db)

        if not user or user.rol != 1:
            return RedirectResponse("/", status_code=302)

        print(f"ID Usuario recibido: {id_usuario}")  # Depuración
        paciente = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
        if not paciente:
            raise HTTPException(status_code=404, detail="El usuario no existe")

        # Crear el expediente clínico
        nuevo_expediente = ExpClinicoPaciente(
            id_usuario=id_usuario,
            anotaciones_nuevas_paciente=anotaciones_nuevas_paciente,
            fecha_cita=datetime.strptime(fecha_cita, "%Y-%m-%dT%H:%M")
        )
        db.add(nuevo_expediente)
        db.commit()

        print("Expediente creado exitosamente")
        return RedirectResponse(f"/users/ver-expediente/{id_usuario}", status_code=302)
    except Exception as e:
        db.rollback()
        print(f"Error al guardar el expediente: {e}")
        return RedirectResponse("/", status_code=302)

@router.delete("/users/eliminar-expediente/{id_expediente}", response_class=JSONResponse)
def eliminar_expediente(
    id_expediente: int,
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="No autorizado")

    try:
        user_data = decode_token(access_token)
        user = get_user(user_data["username"], db)
        if not user or user.rol != 1:
            raise HTTPException(status_code=403, detail="Acceso denegado")
        anotacion = db.query(ExpClinicoPaciente).filter_by(id_expediente=id_expediente).first()
        if anotacion:
            id_usuario = anotacion.id_usuario
            db.delete(anotacion)
            db.commit()
            return JSONResponse(content={"message": "Anotación eliminada exitosamente"}, status_code=200)
        else:
            raise HTTPException(status_code=404, detail="Anotación no encontrada")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {e}")

@router.get("/users/ver-expediente/{id_usuario}", response_class=HTMLResponse)
def ver_expediente(
    id_usuario: int, 
    request: Request,
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token: 
        raise HTTPException(status_code=401, detail="No autorizado")
    
    user_data = decode_token(access_token)
    user = get_user(user_data["username"], db)
    if not user or user.rol != 1:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    # Recuperar las anotaciones y datos del paciente
    paciente = db.query(Usuario).filter_by(id_usuario=id_usuario).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    anotaciones = db.query(ExpClinicoPaciente).filter_by(id_usuario=id_usuario).all()
    
    return templates.TemplateResponse(
        "viewsDoc/expediente.html", 
        {
            "request": request, 
            "anotaciones": anotaciones,
            "paciente": paciente
        }
    )
  
@router.get("/users/actualizar-anotacion/{id_expediente}", response_class=HTMLResponse)
def formulario_actualizar_anotacion(
    id_expediente: int,
    request: Request,
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="No autorizado")

    user_data = decode_token(access_token)
    user = get_user(user_data["username"], db)
    if not user or user.rol != 1:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    anotacion = db.query(ExpClinicoPaciente).filter_by(id_expediente=id_expediente).first()
    if not anotacion:
        raise HTTPException(status_code=404, detail="Anotación no encontrada")

    return templates.TemplateResponse(
        "viewsDoc/actualizar_anotacion.html",
        {"request": request, "anotacion": anotacion}
    )

@router.post("/users/actualizar-anotacion/{id_expediente}", response_class=RedirectResponse)
def actualizar_anotacion(
    id_expediente: int,
    anotaciones_nuevas_paciente: str = Form(...),
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="No autorizado")

    user_data = decode_token(access_token)
    user = get_user(user_data["username"], db)
    if not user or user.rol != 1:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    try:
        anotacion = db.query(ExpClinicoPaciente).filter_by(id_expediente=id_expediente).first()
        if not anotacion:
            raise HTTPException(status_code=404, detail="Anotación no encontrada")

        anotacion.anotaciones_nuevas_paciente = anotaciones_nuevas_paciente
        db.commit()
        return RedirectResponse(f"/users/ver-expediente/{anotacion.id_usuario}", status_code=302)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/users/ver-expediente", response_class=HTMLResponse)
def ver_expediente_usuario(
    request: Request,
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="No autorizado")

    try:
        user_data = decode_token(access_token)
        user = get_user(user_data["username"], db)
        if not user or user.rol != 0:  # rol = 0 para usuarios regulares
            raise HTTPException(status_code=403, detail="Acceso denegado")

        # Obtener anotaciones del expediente clínico
        anotaciones = db.query(ExpClinicoPaciente).filter(ExpClinicoPaciente.id_usuario == user.id_usuario).all()

        return templates.TemplateResponse(
            "viewsU/expediente.html",
            {"request": request, "anotaciones": anotaciones, "user": user}
        )
    except Exception as e:
        print(f"Error al obtener el expediente del usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/users/ver-receta/{id_receta}", response_class=HTMLResponse)
def ver_receta(
    id_receta: int,
    request: Request,
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="No autorizado")
    try:
        # Decodificar el token para obtener el id del médico
        user_data = decode_token(access_token)
        user = get_user(user_data["username"], db)
        if not user or user.rol != 1:
            raise HTTPException(status_code=403, detail="Acceso denegado")
        # Buscar la receta y verificar que pertenece al médico actual
        receta = db.query(RecMedicaPaciente).filter(
            RecMedicaPaciente.id_receta == id_receta,
            RecMedicaPaciente.id_medico == user.id_usuario
        ).first()
        if not receta:
            raise HTTPException(status_code=404, detail="Receta no encontrada o no pertenece al médico actual")
        # Renderizar el formulario de actualización
        return templates.TemplateResponse(
            "viewsDoc/ver_receta.html",
            {"request": request, "receta": receta}
        )
    except Exception as e:
        print(f"Error al cargar el formulario de actualización de receta: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")




    