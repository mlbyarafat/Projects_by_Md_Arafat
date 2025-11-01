import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas, crud
from database import engine, Base, get_db
from typing import List, Optional
import os
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt

# simple settings (for demo); in production read from env vars / secrets manager
SECRET_KEY = os.getenv("SECRET_KEY")
if os.getenv("ENV","development") == "production" and not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is required in production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*7  # 7 days

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Task Manager (Portfolio-ready)")

# Serve static files from 'frontend' directory
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

@app.post("/register", response_model=schemas.UserOut, summary="Register a new user")
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db, user_in)
    return user

@app.post("/token", summary="Get access token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

# Public: list tasks (with optional query)
@app.get("/tasks", response_model=List[schemas.TaskOut], summary="List tasks")
def list_tasks(skip: int = 0, limit: int = 100, q: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.get_tasks(db, skip=skip, limit=limit, q=q)

# Protected: create task (assigns owner)
@app.post("/tasks", response_model=schemas.TaskOut, summary="Create task")
def create_task(task_in: schemas.TaskCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.create_task(db, task_in, owner_id=current_user.id)

@app.put("/tasks/{task_id}", response_model=schemas.TaskOut, summary="Update a task")
def update_task(task_id: int, task_in: schemas.TaskUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # ensure user owns the task
    task = crud.get_task(db, task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found or not yours")
    updated = crud.update_task(db, task_id, task_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@app.delete("/tasks/{task_id}", summary="Delete a task")
def delete_task(task_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found or not yours")
    ok = crud.delete_task(db, task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"detail": "Task deleted"}

# keep a simple root that points to frontend index if present
@app.get("/", include_in_schema=False)
def root():
    index = os.path.join("frontend", "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return {"msg": "FastAPI Task Manager. Visit /docs for API"}


@app.get('/health', tags=['health'])
async def health():
    return {"status":"ok"}
