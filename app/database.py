from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL # Importa la URL de conexión desde .env

# Crea el "motor" de SQLAlchemy que se conectará a tu base de datos
engine = create_engine(DATABASE_URL)

# Crea una fábrica de sesiones que se usará para cada petición a la API
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Una clase Base de la cual heredarán todos tus modelos de base de datos
Base = declarative_base()