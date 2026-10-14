from .ai_models import WorkoutPlan
from .config import settings
from .gemini_client import generate_structured
from .gemini_generator import generate_workout_gemini


async def update_workout_plan(
    username: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
    original_plan: str,
    feedback: str,
) -> str:
    if settings.demo_mode or not settings.gemini_api_key:
        return (
            original_plan
            + "\n\nUPDATED USING FEEDBACK\n"
            + f"Requested changes: {feedback}\n"
            + "Adjustment: Keep the same overall goal and intensity, incorporate the requested "
              "preference, and retain at least one recovery-focused day."
        )

    prompt = f"""
Revise the existing 7-day fitness plan using the user's feedback.

User:
- Name: {username}
- Age: {age}
- Weight: {weight} kg
- Goal: {goal}
- Intensity: {intensity}

Feedback:
{feedback}

Original plan:
{original_plan}

Return a complete replacement plan, not only a list of edits.
Preserve useful parts unless the feedback asks to change them.
Exactly 7 days; each day needs focus, warm-up, exercises with sets/reps or duration, and cooldown/recovery.
Avoid medical diagnosis or treatment and include a sensible safety note.
"""
    return await generate_structured(settings.gemini_pro_model, prompt, WorkoutPlan)
