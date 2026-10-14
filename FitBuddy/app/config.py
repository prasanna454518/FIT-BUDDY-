from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "FitBuddy"
    database_url: str = f"sqlite:///{BASE_DIR / 'fitbuddy.db'}"

    # Current Google GenAI SDK / model defaults. Override in .env as needed.
    gemini_api_key: str = ""
    gemini_pro_model: str = "gemini-2.5-pro"
    gemini_flash_model: str = "gemini-2.5-flash"

    # Set DEMO_MODE=true to run without a Gemini API key.
    demo_mode: bool = True

    session_secret: str = "change-this-secret-in-production"
    admin_username: str = "admin"
    admin_password: str = "fitbuddy-admin"

    templates_dir: str = str(BASE_DIR / "templates")
    static_dir: str = str(BASE_DIR / "static")

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
