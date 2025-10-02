from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select, SQLModel
from typing import List, Annotated
from fastapi.middleware.cors import CORSMiddleware

# Importaciones locales de nuestros propios archivos
from db import get_session, create_db_and_tables
from models import Task

app = FastAPI(title="API de Tareas con FastAPI y RDS")

# --- CONFIGURACIÓN DE CORS ---
# Esto es crucial para permitir que tu frontend (que corre en localhost:3000)
# se comunique con esta API.
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos: GET, POST, PUT, DELETE
    allow_headers=["*"],  # Permite todos los encabezados
)
# -----------------------------------------

@app.on_event("startup")
def on_startup():
    # Esta función se ejecuta una sola vez, cuando la API arranca.
    # Llama a la función de db.py para crear la tabla 'Task' en la base de datos
    # si es que todavía no existe.
    create_db_and_tables()

# Creamos un tipo anotado para no tener que escribir 'Depends(get_session)' en cada endpoint.
# Es una forma más limpia de hacer inyección de dependencias.
SessionDep = Annotated[Session, Depends(get_session)]

# Este es un modelo Pydantic/SQLModel que usamos específicamente para las actualizaciones (PUT).
# Permite que el frontend envíe solo los campos que quiere cambiar, sin necesidad de enviarlos todos.
class TaskUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None

# --- ENDPOINTS CRUD PARA TAREAS ---

@app.post("/tasks/", response_model=Task)
def create_task(task: Task, session: SessionDep):
    """
    Crea una nueva tarea en la base de datos.
    Recibe los datos de la nueva tarea en el cuerpo de la petición.
    """
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.get("/tasks/", response_model=List[Task])
def read_tasks(session: SessionDep):
    """
    Obtiene y devuelve una lista de todas las tareas existentes en la base de datos.
    """
    tasks = session.exec(select(Task)).all()
    return tasks

@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: int, session: SessionDep):
    """
    Obtiene una única tarea específica por su ID.
    El ID se pasa como parte de la URL.
    """
    task = session.get(Task, task_id)
    if not task:
        # Si no se encuentra una tarea con ese ID, devuelve un error 404.
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: TaskUpdate, session: SessionDep):
    """
    Actualiza una tarea existente. Puede actualizar el título, la descripción o el estado 'completed'.
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    # Este bloque de código actualiza solo los campos que el usuario envió.
    # Si el usuario solo envió 'completed', solo se actualizará ese campo.
    task_data = updated_task.model_dump(exclude_unset=True)
    for key, value in task_data.items():
        setattr(task, key, value)
    
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: SessionDep):
    """
    Elimina una tarea de la base de datos usando su ID.
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    session.delete(task)
    session.commit()
    # Devuelve una confirmación de que la operación fue exitosa.
    return {"ok": True}

