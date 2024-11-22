from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database.database import Base, engine

Base.metadata.create_all(bind=engine)

# Inicialización de la aplicación y configuraciones de FastAPI
app = FastAPI()

app.mount("/images", StaticFiles(directory="images"), name="images")

from routes import auth, dashboard, home
app.include_router(home.router)
app.include_router(auth.router)
app.include_router(dashboard.router)