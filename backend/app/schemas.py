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


class StudentProfilePayload(BaseModel):
    age: int = Field(ge=10, le=100)
    weightKg: float = Field(ge=25.0, le=250.0)
    heightCm: float = Field(ge=80.0, le=250.0)
    studyHoursPerDay: float = Field(ge=1.0, le=18.0)


class StudentProfileResponse(BaseModel):
    id: int
    userId: int
    age: int
    weightKg: float
    heightCm: float
    studyHoursPerDay: float
    dailyWaterTargetMl: int
    dailyWorkoutTargetMins: int
    bmi: float
    maintenanceCalories: int
    studySafeRecommendation: str


class StudentDailyLogPayload(BaseModel):
    date: str = Field(min_length=1)
    workoutMinsCompleted: int = Field(ge=0)
    waterMlCompleted: int = Field(ge=0)


class StudentDailyLogResponse(BaseModel):
    id: int
    userId: int
    date: str
    workoutMinsCompleted: int
    waterMlCompleted: int
    status: str
    penaltyCharged: float
    refunded: float


class VaultResponse(BaseModel):
    userId: int
    walletBalance: float
    lockedPenaltyAmount: float
    totalPenalized: float
    totalRefunded: float
    canRedeem: bool
    redemptionMessage: str


class RedeemPenaltyPayload(BaseModel):
    date: str = Field(min_length=1)
    extraWorkoutMins: int = Field(ge=15)

