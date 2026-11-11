from datetime import datetime

from pydantic import BaseModel


class ContentPreview(BaseModel):
    """Conteúdo coletado de uma fonte externa, ainda sem avaliação de IA."""

    external_id: str
    source: str
    title: str
    summary: str | None = None
    authors: list[str] = []
    categories: list[str] = []
    published_at: datetime | None = None
    url: str
    thumbnail_url: str | None = None
    view_count: int | None = None


class FeedPreviewResponse(BaseModel):
    category: str
    count: int
    items: list[ContentPreview]
    # Deixa explícito que não há avaliação de qualidade nesta fase
    evaluated: bool = False
    note: str = (
        "Conteúdos reais coletados do arXiv. Ainda não foram avaliados pela IA: "
        "não há nota de qualidade."
    )
