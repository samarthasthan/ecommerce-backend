from fastapi import FastAPI
from database import engine
import models
from routes import (
    authentication_routes,
    roles_routes,
    addresses_routes,
    category_routes,
    products_routes,
    app_pages_routes,
    carts_routes,
    wishlist_routes
)
from sampledata import samplehomepage

app = FastAPI(title='FruBay')
models.Base.metadata.create_all(engine)

app.include_router(addresses_routes.router)
app.include_router(app_pages_routes.router)
app.include_router(authentication_routes.router)
app.include_router(carts_routes.router)
app.include_router(wishlist_routes.router)
app.include_router(category_routes.router)
app.include_router(products_routes.router)
app.include_router(roles_routes.router)
app.include_router(samplehomepage.router)
