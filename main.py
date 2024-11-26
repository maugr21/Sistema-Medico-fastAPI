from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database.database import Base, engine

Base.metadata.create_all(bind=engine)

# Inicialización de la aplicación y configuraciones de FastAPI
app = FastAPI()

app.mount("/images", StaticFiles(directory="images"), name="images")

from routes import auth, dashboard, home, dashboardDoc, signup
app.include_router(home.router)
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(dashboardDoc.router)
app.include_router(signup.router)
#app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"]) # type: ignore
#app.include_router(dashboard_doc_router, prefix="/dashboard-doc", tags=["Dashboard Doc"])