import os

from fastapi import FastAPI

from app.routers import imports_router, delete_router
from app.utils import ConfigProxy, DatabaseProxy, LoggerProxy


app = FastAPI(title="Yandex Enrollment", version="1.0.0")
app.include_router(imports_router)
app.include_router(delete_router)


@app.on_event("startup")
def startup_application():
    DatabaseProxy.init()
    LoggerProxy().info(f"running in {ConfigProxy.env} environment")
