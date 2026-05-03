from pydantic import BaseModel, Field
from datetime import datetime


class RegisterRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        examples=["Jonh"],
    )

    link: str = Field(
        ...,
        min_length=1,
        examples=["@username"],
    )


class RegisterResponse(BaseModel):
    name: str
    created_at: datetime


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
