from fastapi import FastAPI
from database import engine
import models
from routes import roles_routes
app=FastAPI()

models.Base.metadata.create_all(engine)

app.include_router(roles_routes.router)