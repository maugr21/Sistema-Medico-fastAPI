from .database import Base, engine
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, Date

class Usuario(Base):
    __tablename__='usuarios'
    id_usuario=Column(Integer, primary_key=True, index=True)
    nombre=Column(String, index=True)
    apellido=Column(String)
    email=Column(String, unique=True, index=True)
    fecha_nacimiento = Column(Date)
    password = Column(String)
    rol = Column(String)
    cedula_profesional = Column(String, unique=True)
    especialidad = Column(String)
    
class CitaMedica(Base):
    __tablename__='cita_medica'
    id_cita = Column(Integer, primary_key=True, index=True)
    id_usuario=Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=False)
    id_medico = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=False)
    fecha_cita=Column(DateTime, nullable=False)
    confirm_cita=Column(Boolean, default=False)