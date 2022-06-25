from fastapi import FastAPI, Response
from fastapi.exceptions import RequestValidationError

import app.schemas as s

from app.routers import imports_router, delete_router, nodes_router, sales_router
from app.utils import DatabaseProxy


app = FastAPI(title="Yandex Enrollment", version="1.0.0")
app.include_router(imports_router)
app.include_router(delete_router)
app.include_router(nodes_router)
app.include_router(sales_router)


@app.get("/ping", tags=["State"])
def ping():
    return {"msg": "pong"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    error = s.Error(code=400, message="Validation Failed")
    return Response(content=error.json(), status_code=400, headers={
        "Content-Type": "application/json",
    })


@app.on_event("startup")
def startup_application():
    DatabaseProxy.init()
