from .ai_models import NutritionTip
from .config import settings
from .gemini_client import generate_structured


def _demo_tip(goal: str) -> str:
    tips = {
        "weight loss": "Build meals around vegetables, a protein source, whole-food carbohydrates, and sensible portions.",
        "muscle gain": "Include a protein-rich food in each meal and eat enough overall to support training and recovery.",
        "general wellness": "Stay hydrated, include a variety of minimally processed foods, and keep regular meal timing.",
        "flexibility": "Support recovery with adequate fluids and balanced meals containing protein, produce, and whole-food carbohydrates.",
    }
    return tips.get(goal, tips["general wellness"])


async def generate_nutrition_tip_with_flash(goal: str) -> str:
    if settings.demo_mode or not settings.gemini_api_key:
        return _demo_tip(goal)

    prompt = f"""
Give one concise nutrition or recovery tip for a general fitness user whose goal is "{goal}".
Keep it practical, non-medical, and avoid individualized calorie or medical advice.
"""
    result = await generate_structured(settings.gemini_flash_model, prompt, NutritionTip)
    return result
