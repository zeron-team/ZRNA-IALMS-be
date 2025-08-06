from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- Base de Datos ---
from app import db_models
from app.database import engine

# --- Routers ---
# 1. Importa los nuevos routers 'categories' y 'learning_paths'
from app.routers import (
    auth,
    users,
    courses,
    modules,
    roles,
    enrollments,
    admin,
    categories,
    learning_paths,
    dashboard,
    quizzes
)

# Crea todas las tablas en la base de datos si no existen al iniciar la app
db_models.Base.metadata.create_all(bind=engine)


# --- Inicialización de la App ---
app = FastAPI(
    title="IA LMS Profesional",
    description="Backend para un Sistema de Gestión de Aprendizaje con IA.",
    version="1.0.0"
)


# --- Middleware ---
# Configuración de CORS para permitir que el frontend se conecte
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Inclusión de Routers ---
# Aquí le decimos a la aplicación principal que use las rutas de cada módulo
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(modules.router)
app.include_router(roles.router)
app.include_router(enrollments.router)
app.include_router(admin.router)
app.include_router(categories.router)
app.include_router(learning_paths.router)
app.include_router(dashboard.router)
app.include_router(quizzes.router)


# --- Ruta Raíz ---
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido al API de IA LMS"}