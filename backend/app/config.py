from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://immigration:immigration_dev@localhost:5433/immigration_roadmap"
    anthropic_api_key: str = ""
    nextauth_secret: str = "change-me"
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"

    model_config = {"env_file": "../.env", "extra": "ignore"}

    @model_validator(mode="after")
    def fix_database_url(self):
        # Railway provides postgresql:// but we need postgresql+asyncpg://
        if self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )
        return self


settings = Settings()
