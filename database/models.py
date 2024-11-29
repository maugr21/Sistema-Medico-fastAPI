from datetime import datetime
from typing import Text
from .database import Base, engine
from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, Date, Text

class CitaMedica(Base):
    __tablename__ = 'cita_medica'
    id_cita = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=False)
    id_medico = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=False)
    fecha_cita = Column(DateTime, nullable=False)
    confirm_cita = Column(Boolean, default=False)
    usuario = relationship("Usuario", foreign_keys=[id_usuario])
    medico = relationship("Usuario", foreign_keys=[id_medico])
    receta = relationship("RecMedicaPaciente", back_populates="cita", uselist=False)

class RecMedicaPaciente(Base):
    __tablename__ = 'Rec_Medica_Paciente'
    id_receta = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    id_medico = Column(Integer, ForeignKey("usuarios.id_usuario"))
    id_cita = Column(Integer, ForeignKey("cita_medica.id_cita"))  # Cambié de "CitaMedica" a "cita_medica"
    anotaciones_receta_paciente = Column(Text, nullable=False)
    fecha_cita = Column(DateTime)
    cita = relationship("CitaMedica", foreign_keys=[id_cita])
    medico=relationship("Usuario",foreign_keys=[id_medico])
    usuario = relationship("Usuario", foreign_keys=[id_usuario])

class Usuario(Base):
    __tablename__ = 'usuarios'
    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    apellido = Column(String)
    email = Column(String, unique=True, index=True)
    fecha_nacimiento = Column(Date)
    password = Column(String)
    rol = Column(String)
    cedula_profesional = Column(String, unique=True)
    especialidad = Column(String)

class ExpClinicoPaciente(Base):
    __tablename__ = 'exp_clinico_paciente'
    id_expediente = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    anotaciones_nuevas_paciente = Column(Text)
    fecha_cita = Column(DateTime, nullable=True)
