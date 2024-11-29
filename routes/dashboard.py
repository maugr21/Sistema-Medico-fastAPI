from datetime import datetime, timedelta
from fastapi import APIRouter, Form, HTTPException, Request, Cookie, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from database.models import ExpClinicoPaciente, RecMedicaPaciente, Usuario, CitaMedica
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


@router.get("/users/dashboard-user", response_class=HTMLResponse)
def dashboard_user(
    request: Request,
    especialidad: str | None = None,  
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

        query = db.query(Usuario).filter(Usuario.rol == 1)
        if especialidad:
            query = query.filter(Usuario.especialidad.ilike(f"%{especialidad}%"))
        
        doctors = query.all()
        return templates.TemplateResponse("viewsU/dashboard.html", {"request": request, "users": doctors})
    except Exception as e:
        print(f"Error al obtener médicos: {e}")
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
def agendarCitaForm(
    id_usuario: int, 
    request: Request, 
    access_token: str | None = Cookie(None), 
    db: Session = Depends(get_db)
):
    if not access_token:
        return RedirectResponse("/", status_code=302)
    try:
        user_data = decode_token(access_token)
        user = get_user(user_data["username"], db)
        if not user:
            return RedirectResponse("/", status_code=302)
        medico = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
        today = datetime.now().date()
        citas = db.query(CitaMedica).filter(
            CitaMedica.id_medico == id_usuario,
            CitaMedica.fecha_cita >= today,
            CitaMedica.fecha_cita < today + timedelta(days=1)
        ).all()
        ocupadas = [cita.fecha_cita.strftime("%Y-%m-%dT%H:%M") for cita in citas]
        available_hours = []
        for hour in range(8, 18):
            for minute in [0]:
                datetime_str = f"{today}T{hour:02d}:{minute:02d}"
                if datetime_str not in ocupadas:
                    available_hours.append(datetime_str)
        return templates.TemplateResponse("viewsU/AgendarCita.html", {
            "request": request, 
            "id_usuario": id_usuario, 
            "medico": medico,
            "available_hours": available_hours 
        })
    except Exception as e: 
        print(f"Error: {e}")
        return RedirectResponse("/", status_code=302)

    

@router.post("/users/agendarCita/{id_usuario}", response_class=HTMLResponse)
def agendarCita(
    id_usuario: int,  # ID del médico
    request: Request, 
    access_token: str | None = Cookie(None), 
    fecha_cita: str = Form(...),  # Fecha seleccionada en el formulario
    hora_cita: str = Form(...),   # Hora seleccionada en el formulario
    db: Session = Depends(get_db)
):
    if not access_token:
        return RedirectResponse("/", status_code=302)
    try:
        user_data = decode_token(access_token)
        user = get_user(user_data["username"], db)
        if not user:
            return RedirectResponse("/", status_code=302)
        id_paciente = user.id_usuario 
        medico = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
        if not medico:
            return JSONResponse(content={"error": "El médico seleccionado no existe."}, status_code=400)
        if "T" in hora_cita:
            hora_cita = hora_cita.split("T")[1]
        cita_str = f"{fecha_cita}T{hora_cita}:00"
        print(f"Fecha y hora combinadas: {cita_str}")
        cita_existente = db.query(CitaMedica).filter(CitaMedica.fecha_cita == cita_str).first()
        if cita_existente:
            return JSONResponse(content={"error": "La hora seleccionada ya está ocupada."}, status_code=409)
        nueva_cita = CitaMedica(
            id_medico=id_usuario,
            id_usuario=id_paciente,
            fecha_cita=cita_str
        )
        db.add(nueva_cita)
        db.commit()
        return RedirectResponse(f"/users/agendarCita/{id_usuario}", status_code=302)
    except Exception as e:
        print(f"Error: {e}")
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
        anotaciones = db.query(ExpClinicoPaciente).filter(ExpClinicoPaciente.id_usuario == user.id_usuario).all()

        return templates.TemplateResponse(
            "viewsU/expediente.html",
            {"request": request, "anotaciones": anotaciones, "user": user}
        )
    except Exception as e:
        print(f"Error al obtener el expediente del usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/users/ver-receta-cliente/{id_receta}", response_class=HTMLResponse)
def ver_receta_cliente(
    id_receta: int,
    request: Request,
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="No autorizado")
    try:
        # Decodificar el token para obtener el id del paciente
        user_data = decode_token(access_token)
        user = get_user(user_data["username"], db)

        if not user or user.rol != 0:  # Asegúrate de que el rol 2 corresponde a "paciente"
            raise HTTPException(status_code=403, detail="Acceso denegado")

        # Buscar la receta y verificar que pertenece al paciente actual
        receta = (
            db.query(RecMedicaPaciente)
            .join(CitaMedica, RecMedicaPaciente.id_cita == CitaMedica.id_cita)
            .filter(
                RecMedicaPaciente.id_receta == id_receta,
                CitaMedica.id_usuario == user.id_usuario 
            )
            .first()
        )
        if not receta:
            raise HTTPException(status_code=404, detail="Receta no encontrada o no pertenece al paciente actual")

        # Renderizar la vista
        return templates.TemplateResponse(
            "viewsU/receta.html",
            {"request": request, "receta": receta}
        )
    except Exception as e:
        print(f"Error al cargar la receta para el cliente: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")





    
