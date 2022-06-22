from fastapi import FastAPI

from app.routers import imports_router
from app.models import Base
from app.dependencies import engine

app = FastAPI(title="Yandex Enrollment", version="1.0.0")
app.include_router(imports_router)


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)
