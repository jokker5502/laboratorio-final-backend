from sqlmodel import create_engine, SQLModel, Session
import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Lee las credenciales de la base de datos de forma segura
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")

# Construye la URL de conexión para PostgreSQL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Crea el "motor" de SQLAlchemy que gestionará la conexión
engine = create_engine(DATABASE_URL, echo=True)

# Función que se ejecutará al iniciar la API para crear las tablas si no existen
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Función que proporciona una sesión de base de datos a los endpoints
def get_session():
    with Session(engine) as session:
        yield session
