"""Configuração central da aplicação, lida de variáveis de ambiente (.env)."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# .env fica na raiz do projeto (dois níveis acima de backend/app/core)
ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Plataforma de Curadoria Inteligente"
    environment: str = "development"
    debug: bool = False

    # Banco de dados (usado a partir da Etapa 2)
    database_url: str = "postgresql+psycopg://curadoria:curadoria@localhost:5432/curadoria"

    # Segurança (usado a partir da Etapa 5). Sem valor padrão seguro: deve ser definido no .env.
    secret_key: str = Field(default="", repr=False)
    access_token_expire_minutes: int = 60

    # CORS: origens permitidas do frontend, separadas por vírgula
    cors_origins: str = "http://localhost:3000"

    # Integrações externas (opcionais nesta etapa; nunca expostas ao frontend)
    youtube_api_key: str = Field(default="", repr=False)
    llm_provider: str = "anthropic"
    llm_api_key: str = Field(default="", repr=False)
    llm_model: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
