from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud
from ..dependencies import get_db, get_current_user
from ..models import User

router = APIRouter(prefix="/todos", tags=["todos"])

@router.post("/", response_model=schemas.TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(
    todo: schemas.TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.create_todo(db, todo, owner_id=current_user.id)

@router.get("/", response_model=List[schemas.TodoResponse])
def read_todos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    todos = crud.get_todos(db, owner_id=current_user.id, skip=skip, limit=limit)
    return todos

@router.get("/{todo_id}", response_model=schemas.TodoResponse)
def read_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_todo = crud.get_todo(db, todo_id, owner_id=current_user.id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

@router.put("/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(
    todo_id: int,
    todo_update: schemas.TodoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_todo = crud.update_todo(db, todo_id, current_user.id, todo_update)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = crud.delete_todo(db, todo_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Todo not found")