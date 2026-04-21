import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s', force=True)
from fastapi import FastAPI
import models
from database import engine
from routers import auth, todos, admin, users, gemini


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)

app.include_router(admin.router)

app.include_router(users.router)

app.include_router(gemini.router)