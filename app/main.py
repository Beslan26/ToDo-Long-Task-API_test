from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from uuid import uuid4

from app.database import Base, engine
from app.database import get_db
from app.models import Task
from app.schemas import TaskCreate, TaskUpdate, TaskOut
from app.tasks import long_running_task, progress_store

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/tasks", response_model=list[TaskOut])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()


@app.post("/tasks", response_model=TaskOut)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(
        task_id: int,
        updates: TaskUpdate,
        db: Session = Depends(get_db)
):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    for key, value in updates.dict(exclude_unset=True).items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"ok": True}


# Асинхронная задача
@app.post("/long-task/")
async def start_long_task(background_tasks: BackgroundTasks):
    task_id = str(uuid4())
    progress_store[task_id] = 0
    background_tasks.add_task(long_running_task, task_id)
    return {"task_id": task_id}


@app.get("/long-task/{task_id}")
def get_progress(task_id: str):
    progress = progress_store.get(task_id)
    if progress is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task_id": task_id, "progress": progress}
