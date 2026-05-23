from sqlalchemy.orm import Session
from . import models, schemas
from .security import get_password_hash, verify_password

def get_todo(db: Session, todo_id: int):
    return db.query(models.Todo).filter(models.Todo.id == todo_id).first()

def get_todo(db: Session, todo_id: int, owner_id: int):
    return db.query(models.Todo).filter(
        models.Todo.id == todo_id,
        models.Todo.owner_id == owner_id
    ).first()


def create_todo(db: Session, todo: schemas.TodoCreate, owner_id: int):
    db_todo = models.Todo(
        title=todo.title, 
        description=todo.description,
        owner_id=owner_id
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def update_todo(db: Session, todo_id: int, todo_update: schemas.TodoUpdate):
    db_todo = get_todo(db, todo_id)
    if not db_todo:
        return None
    for var, value in vars(todo_update).items():
        if value is not None:
            setattr(db_todo, var, value)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def delete_todo(db: Session, todo_id: int):
    db_todo = get_todo(db, todo_id)
    if db_todo:
        db.delete(db_todo)
        db.commit()
        return True
    return False

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
