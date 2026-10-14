from .ai_models import WorkoutPlan
from .config import settings
from .gemini_client import generate_structured


def _demo_plan(username: str, age: int, weight: float, goal: str, intensity: str) -> str:
    effort = {"low": "comfortable", "medium": "moderate", "high": "challenging"}[intensity]
    focuses = [
        ("Day 1", "Full Body"),
        ("Day 2", "Cardio"),
        ("Day 3", "Lower Body"),
        ("Day 4", "Recovery & Mobility"),
        ("Day 5", "Upper Body"),
        ("Day 6", "Core + Cardio"),
        ("Day 7", "Active Recovery"),
    ]
    lines = [
        f"FITBUDDY 7-DAY PLAN FOR {username.upper()}",
        f"Goal: {goal.title()} | Intensity: {intensity.title()} | Weight: {weight:g} kg | Age: {age}",
        "",
        "Safety note: Start gradually, use good form, hydrate, and stop if you feel pain or become unwell.",
    ]
    for day, focus in focuses:
        lines += [
            "",
            f"{day} — {focus}",
            "Warm-up: 5–10 minutes of easy movement and dynamic mobility.",
            f"Main workout: 3–4 exercises, 2–3 sets each, at a {effort} effort appropriate to your level.",
            "Example: bodyweight squat, incline push-up, glute bridge, row/band pull-apart.",
            "Rest: 45–90 seconds between sets.",
            "Cooldown: 5–10 minutes of easy movement and gentle stretching.",
        ]
    return "\n".join(lines)


async def generate_workout_gemini(
    username: str, age: int, weight: float, goal: str, intensity: str
) -> str:
    if settings.demo_mode or not settings.gemini_api_key:
        return _demo_plan(username, age, weight, goal, intensity)

    prompt = f"""
Create a safe, practical, personalized 7-day beginner-to-intermediate fitness plan.

User:
- Name: {username}
- Age: {age}
- Weight: {weight} kg
- Goal: {goal}
- Preferred intensity: {intensity}

Requirements:
- Exactly 7 days.
- Every day must include a focus, 5–10 minute warm-up, main exercises with sets/reps or duration,
  and a cooldown/recovery instruction.
- Include rest/recovery where appropriate.
- Avoid diagnosing medical conditions or prescribing treatment.
- Do not promise specific weight-loss or muscle-gain outcomes.
- Keep the plan realistic for a general user.
- Mention that users with medical conditions, injuries, pregnancy, or exercise restrictions should
  consult an appropriate healthcare professional before starting.
"""
    return await generate_structured(settings.gemini_pro_model, prompt, WorkoutPlan)
