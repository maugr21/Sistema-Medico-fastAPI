from sqlalchemy import Column,Integer, String, Boolean, Date,create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


#Configuración de la URL de la base de datos
#URL="mysql+pymysql://FastApi:root@localhost/sistema_medico"
URL="mysql+pymysql://root:admin@localhost/SistemaClinico"


#Motor de Conexión
engine=create_engine(URL, connect_args={"charset":"utf8mb4"})
#Base para las clases de los modelos
Base=declarative_base()
SessionLocal=sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SessionLocal()
print("Conexión a la base de datos exitosa")
db.close()


# Dependencia para obtener una sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()