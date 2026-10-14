from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from .config import settings
from .database import (
    delete_user,
    get_all_users,
    get_plan,
    get_user,
    init_db,
    save_plan,
    save_user,
    update_plan,
)
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .gemini_generator import generate_workout_gemini
from .schemas import FeedbackRequest, UserInput
from .updated_plan import update_workout_plan


router = APIRouter()
templates = Jinja2Templates(directory=settings.templates_dir)
init_db()


def page_context(request: Request, **kwargs):
    return {"request": request, **kwargs}


def admin_required(request: Request) -> bool:
    return bool(request.session.get("admin_authenticated"))


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html", page_context(request, error=None),
    )


@router.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name}


@router.post("/generate-workout", response_class=HTMLResponse)
async def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
):
    try:
        data = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )
    except ValidationError as exc:
        message = exc.errors()[0].get("msg", "Please check your input.")
        return templates.TemplateResponse(request, "index.html", page_context(request, error=message, form=request._form if hasattr(request, "_form") else None),
            status_code=422,
        )

    existing = get_user(data.user_id)
    if existing:
        return templates.TemplateResponse(
            request,
            "index.html",
            page_context(
                request,
                error=f"User ID '{data.user_id}' already exists. Use another ID or open the existing plan.",
            ),
            status_code=409,
        )

    try:
        workout = await generate_workout_gemini(
            data.username, data.age, data.weight, data.goal, data.intensity
        )
        tip = await generate_nutrition_tip_with_flash(data.goal)
    except Exception as exc:
        return templates.TemplateResponse(
            "index.html",
            page_context(
                request,
                error=f"AI generation failed: {exc}. Check your Gemini API key/model settings.",
            ),
            status_code=502,
        )

    save_user(data.model_dump())
    save_plan(data.user_id, workout, tip)

    return templates.TemplateResponse(
        request,
        "result.html",
        page_context(
            request,
            user=data,
            workout_plan=workout,
            nutrition_tip=tip,
            feedback=None,
            updated=False,
        ),
    )


@router.get("/plan/{user_id}", response_class=HTMLResponse)
async def view_plan(request: Request, user_id: str):
    user = get_user(user_id)
    plan = get_plan(user_id)
    if not user or not plan:
        raise HTTPException(status_code=404, detail="User or plan not found.")

    active_plan = plan.updated_plan or plan.original_plan
    return templates.TemplateResponse(
        request,
        "result.html",
        page_context(
            request,
            user=user,
            workout_plan=active_plan,
            original_plan=plan.original_plan,
            nutrition_tip=plan.nutrition_tip,
            feedback=plan.feedback,
            updated=bool(plan.updated_plan),
        ),
    )


@router.post("/submit-feedback", response_class=HTMLResponse)
async def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
):
    try:
        data = FeedbackRequest(user_id=user_id, feedback=feedback)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors())

    user = get_user(data.user_id)
    plan = get_plan(data.user_id)
    if not user or not plan:
        raise HTTPException(status_code=404, detail="User or plan not found.")

    try:
        revised = await update_workout_plan(
            user.username,
            user.age,
            user.weight,
            user.goal,
            user.intensity,
            plan.original_plan,
            data.feedback,
        )
        tip = await generate_nutrition_tip_with_flash(user.goal)
    except Exception as exc:
        return templates.TemplateResponse(
            request,
            "result.html",
            page_context(
                request,
                user=user,
                workout_plan=plan.updated_plan or plan.original_plan,
                original_plan=plan.original_plan,
                nutrition_tip=plan.nutrition_tip,
                feedback=data.feedback,
                updated=bool(plan.updated_plan),
                error=f"AI update failed: {exc}",
            ),
            status_code=502,
        )

    updated = update_plan(data.user_id, revised, data.feedback, tip)

    return templates.TemplateResponse(
        request,
        "result.html",
        page_context(
            request,
            user=user,
            workout_plan=updated.updated_plan,
            original_plan=updated.original_plan,
            nutrition_tip=updated.nutrition_tip,
            feedback=updated.feedback,
            updated=True,
            success="Your plan was updated using your feedback.",
        ),
    )


@router.get("/view-all-users", response_class=HTMLResponse)
async def view_all_users(request: Request):
    if not admin_required(request):
        return RedirectResponse("/admin/login", status_code=303)

    users = get_all_users()
    plans = {user.user_id: get_plan(user.user_id) for user in users}
    return templates.TemplateResponse(request, "all_users.html", page_context(request, users=users, plans=plans),
    )


@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse(request, "admin_login.html", page_context(request, error=None),
    )


@router.post("/admin/login", response_class=HTMLResponse)
async def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    if username == settings.admin_username and password == settings.admin_password:
        request.session["admin_authenticated"] = True
        return RedirectResponse("/view-all-users", status_code=303)

    return templates.TemplateResponse(request, "admin_login.html", page_context(request, error="Invalid admin credentials."),
        status_code=401,
    )


@router.post("/admin/logout")
async def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@router.post("/admin/delete/{user_id}")
async def admin_delete(request: Request, user_id: str):
    if not admin_required(request):
        raise HTTPException(status_code=401, detail="Admin authentication required.")
    delete_user(user_id)
    return RedirectResponse("/view-all-users", status_code=303)


# JSON API: useful for Postman, frontend integrations, or mobile clients.
@router.get("/api/users/{user_id}")
async def api_get_user(user_id: str):
    user = get_user(user_id)
    plan = get_plan(user_id)
    if not user or not plan:
        raise HTTPException(status_code=404, detail="User or plan not found.")

    return {
        "user": {
            "user_id": user.user_id,
            "username": user.username,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
        },
        "plan": {
            "original_plan": plan.original_plan,
            "updated_plan": plan.updated_plan,
            "nutrition_tip": plan.nutrition_tip,
            "feedback": plan.feedback,
        },
    }


@router.post("/api/generate-workout")
async def api_generate_workout(data: UserInput):
    if get_user(data.user_id):
        raise HTTPException(status_code=409, detail="User ID already exists.")

    workout = await generate_workout_gemini(
        data.username, data.age, data.weight, data.goal, data.intensity
    )
    tip = await generate_nutrition_tip_with_flash(data.goal)
    save_user(data.model_dump())
    save_plan(data.user_id, workout, tip)

    return {
        "user": data.model_dump(),
        "workout_plan": workout,
        "nutrition_tip": tip,
    }


@router.post("/api/submit-feedback")
async def api_submit_feedback(data: FeedbackRequest):
    user = get_user(data.user_id)
    plan = get_plan(data.user_id)
    if not user or not plan:
        raise HTTPException(status_code=404, detail="User or plan not found.")

    revised = await update_workout_plan(
        user.username,
        user.age,
        user.weight,
        user.goal,
        user.intensity,
        plan.original_plan,
        data.feedback,
    )
    tip = await generate_nutrition_tip_with_flash(user.goal)
    update_plan(data.user_id, revised, data.feedback, tip)

    return {
        "user_id": data.user_id,
        "updated_plan": revised,
        "nutrition_tip": tip,
    }
