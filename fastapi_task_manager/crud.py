from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import List, Optional
import models, schemas

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    """Return a securely hashed version of the password."""
    return pwd_context.hash(password)


# ========================
# USER CRUD OPERATIONS
# ========================

def create_user(db: Session, user: schemas.UserCreate):
    """Create a new user with a hashed password."""
    hashed = get_password_hash(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Fetch a user by email."""
    return db.query(models.User).filter(models.User.email == email).first()


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Fetch a user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def list_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Return a paginated list of users."""
    return db.query(models.User).offset(skip).limit(limit).all()


# ========================
# TASK CRUD OPERATIONS
# ========================

def create_task(db: Session, owner_id: int, task: schemas.TaskCreate):
    """Create a new task for a given owner."""
    db_task = models.Task(**task.dict(), owner_id=owner_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task(db: Session, task_id: int):
    """Retrieve a single task by ID."""
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def get_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    q: Optional[str] = None,
    is_done: Optional[bool] = None
):
    """
    Retrieve multiple tasks, optionally filtered by search term or completion status.
    - q: search by task title (case-insensitive)
    - is_done: True / False filter
    """
    query = db.query(models.Task)
    if q:
        query = query.filter(models.Task.title.ilike(f"%{q}%"))
    if is_done is not None:
        query = query.filter(models.Task.is_done == is_done)
    return query.offset(skip).limit(limit).all()


def update_task(db: Session, task_id: int, task_in: schemas.TaskUpdate):
    """Update an existing task by ID."""
    db_task = get_task(db, task_id)
    if not db_task:
        return None

    for key, value in task_in.dict(exclude_unset=True).items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int):
    """Delete a task by ID."""
    db_task = get_task(db, task_id)
    if not db_task:
        return False
    db.delete(db_task)
    db.commit()
    return True
