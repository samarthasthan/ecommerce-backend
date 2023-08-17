from fastapi import FastAPI
from database import engine
import models
from routes import auth_routes, roles_routes,addresses_routes,category_routes,products_routes
app=FastAPI()
models.Base.metadata.create_all(engine)

app.include_router(products_routes.router)
app.include_router(category_routes.router)
app.include_router(addresses_routes.router)
app.include_router(roles_routes.router)
app.include_router(auth_routes.router)