from typing import Optional
from sqlmodel import Field, SQLModel

class Task(SQLModel, table=True):
    # El ID es opcional porque la base de datos lo generará automáticamente.
    # Es la clave primaria de la tabla.
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # El título de la tarea, es un campo de texto obligatorio.
    title: str
    
    # La descripción es opcional, puede ser nula.
    description: Optional[str] = None
    
    # El estado de completado, por defecto es 'false' cuando se crea una nueva tarea.
    completed: bool = Field(default=False)
