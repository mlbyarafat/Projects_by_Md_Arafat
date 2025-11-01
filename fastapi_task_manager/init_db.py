from database import engine, Base, SessionLocal
import models, crud, schemas
import datetime

def init():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # create sample users
    alice = schemas.UserCreate(name="Alice Example", email="alice@example.com", password="alicepass")
    bob = schemas.UserCreate(name="Bob Example", email="bob@example.com", password="bobpass")
    a = crud.get_user_by_email(db, alice.email)
    if not a:
        a = crud.create_user(db, alice)
    b = crud.get_user_by_email(db, bob.email)
    if not b:
        b = crud.create_user(db, bob)

    # sample tasks
    if len(db.query(models.Task).all()) == 0:
        crud.create_task(db, a.id, schemas.TaskCreate(title="Buy groceries", description="Milk, eggs, bread", is_done=False, due_date=datetime.datetime.utcnow()))
        crud.create_task(db, a.id, schemas.TaskCreate(title="Prepare presentation", description="For Monday meeting", is_done=False))
        crud.create_task(db, b.id, schemas.TaskCreate(title="Fix bug #123", description="Null pointer issue", is_done=True))

    db.close()
    print("Initialized database with sample users and tasks.")

if __name__ == "__main__":
    init()