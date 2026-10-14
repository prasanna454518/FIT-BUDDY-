from pydantic import BaseModel, Field


class WorkoutDay(BaseModel):
    day: str
    focus: str
    warm_up: list[str] = Field(min_length=1)
    exercises: list[str] = Field(min_length=1)
    cooldown: list[str] = Field(min_length=1)


class WorkoutPlan(BaseModel):
    title: str
    safety_note: str
    days: list[WorkoutDay] = Field(min_length=7, max_length=7)


class NutritionTip(BaseModel):
    tip: str
    why_it_helps: str
    practical_action: str
