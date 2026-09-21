from pydantic import BaseModel, Field
from datetime import datetime


class RegisterRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        examples=["Jonh"],
    )

    tg: str = Field(
        ...,
        min_length=1,
        examples=["@username"],
    )

    birthdate: str | None = Field(None)
    city: str | None = Field(None)
    expectations: str | None = Field(None)
    experience: str | None = Field(None)
    github: str | None = Field(None)
    university: str | None = Field(None)


class RegisterResponse(BaseModel):
    name: str
    created_at: datetime


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
