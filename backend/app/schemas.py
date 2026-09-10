from __future__ import annotations

from pydantic import BaseModel, Field


class LoginPayload(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=1)


class UserResponse(BaseModel):
    id: int
    name: str
    email: str


class LoginResponse(BaseModel):
    token: str
    user: UserResponse


class WorkoutPayload(BaseModel):
    day: str = Field(min_length=1)
    focus: str = Field(min_length=1)
    duration: int = Field(ge=1)
    exercises: list[str]


class ProgressPayload(BaseModel):
    date: str = Field(min_length=1)
    minutes: int = Field(ge=1)
    calories: int = Field(ge=1)


class GoalPayload(BaseModel):
    title: str = Field(min_length=1)
    metric: str = Field(min_length=1)
    targetValue: int = Field(ge=1)
    currentValue: int = Field(ge=0)
    deadline: str | None = None
    status: str = Field(min_length=1)
