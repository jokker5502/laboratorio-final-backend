# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from db import get_session, create_db_and_tables
from models import Task

app = FastAPI(title="API de Tareas con FastAPI y RDS")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Endpoint para crear una tarea
@app.post("/tasks/", response_model=Task)
def create_task(task: Task, session: Session = Depends(get_session)):
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

# Endpoint para listar todas las tareas
@app.get("/tasks/", response_model=List[Task])
def read_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(Task)).all()
    return tasks

# Endpoint para obtener una tarea por ID
@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task

# Endpoint para actualizar una tarea
@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: Task, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    task.title = updated_task.title
    task.description = updated_task.description
    task.completed = updated_task.completed
    
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

# Endpoint para eliminar una tarea
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    session.delete(task)
    session.commit()
    return {"ok": True}