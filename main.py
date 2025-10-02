from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select, SQLModel  # <- AQUÍ ESTÁ LA CORRECCIÓN
from typing import List, Annotated
from fastapi.middleware.cors import CORSMiddleware  # <- 1. IMPORTAR CORS

from db import get_session, create_db_and_tables
from models import Task

app = FastAPI(title="API de Tareas con FastAPI y RDS")

# --- 2. AÑADIR LA CONFIGURACIÓN DE CORS ---
origins = [
    "http://localhost:3000",  # El origen de tu app de React
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)
# -----------------------------------------

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

SessionDep = Annotated[Session, Depends(get_session)]

class TaskUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None

@app.post("/tasks/", response_model=Task)
def create_task(task: Task, session: SessionDep):
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.get("/tasks/", response_model=List[Task])
def read_tasks(session: SessionDep):
    tasks = session.exec(select(Task)).all()
    return tasks

@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: int, session: SessionDep):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: TaskUpdate, session: SessionDep):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    task_data = updated_task.model_dump(exclude_unset=True)
    for key, value in task_data.items():
        setattr(task, key, value)
    
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: SessionDep):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    session.delete(task)
    session.commit()
    return {"ok": True}

