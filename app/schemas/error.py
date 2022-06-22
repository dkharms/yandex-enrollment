from pydantic import BaseModel, Field


class Error(BaseModel):
    code: int = Field(description="Status code.")
    message: str = Field(description="Error message.")
