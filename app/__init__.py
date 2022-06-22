from fastapi import FastAPI

from app.models import Base
from app.dependencies import engine

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Yandex Enrollment", version="1.0.0")
