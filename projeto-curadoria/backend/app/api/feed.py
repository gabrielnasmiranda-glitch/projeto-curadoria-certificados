import time
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.collectors.arxiv import ALLOWED_CATEGORIES, CollectorError, fetch_arxiv
from app.collectors.youtube import TOPICS, MissingApiKeyError, fetch_youtube
from app.core.config import get_settings
from app.schemas.content import ContentPreview, FeedPreviewResponse

router = APIRouter(prefix="/feed", tags=["feed"])

# Cache em memória: respeita limites das fontes e economiza cota do YouTube
# (cada busca custa 100 unidades). Será substituído pelo banco na Etapa 3.
CACHE_TTL_SECONDS = 600
_cache: dict[tuple, tuple[float, list[ContentPreview]]] = {}


def _cached(key: tuple, loader) -> list[ContentPreview]:
    cached = _cache.get(key)
    now = time.monotonic()
    if cached and now - cached[0] < CACHE_TTL_SECONDS:
        return cached[1]
    items = loader()
    _cache[key] = (now, items)
    return items


def _get_items(category: str, limit: int) -> list[ContentPreview]:
    return _cached(("arxiv", category, limit), lambda: fetch_arxiv(category, limit))


@router.get("/categories")
def list_categories() -> dict[str, str]:
    """Categorias do arXiv disponíveis no mini feed."""
    return ALLOWED_CATEGORIES


@router.get("/preview", response_model=FeedPreviewResponse)
def feed_preview(
    category: Annotated[str, Query()] = "cs.AI",
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
) -> FeedPreviewResponse:
    """Mini feed com conteúdos reais do arXiv, sem avaliação de IA (ainda)."""
    if category not in ALLOWED_CATEGORIES:
        raise HTTPException(status_code=422, detail="Categoria inválida.")
    try:
        items = _get_items(category, limit)
    except CollectorError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return FeedPreviewResponse(category=category, count=len(items), items=items)


@router.get("/youtube/topics")
def list_youtube_topics() -> dict[str, str]:
    """Tópicos (em português) disponíveis no feed do YouTube."""
    return {key: label for key, (label, _query) in TOPICS.items()}


@router.get("/youtube", response_model=FeedPreviewResponse)
def youtube_feed(
    topic: Annotated[str, Query()] = "ia",
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
) -> FeedPreviewResponse:
    """Vídeos reais em português do YouTube (API oficial), sem avaliação de IA (ainda)."""
    if topic not in TOPICS:
        raise HTTPException(status_code=422, detail="Tópico inválido.")
    api_key = get_settings().youtube_api_key
    try:
        items = _cached(
            ("youtube", topic, limit), lambda: fetch_youtube(api_key, topic, limit)
        )
    except MissingApiKeyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except CollectorError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return FeedPreviewResponse(
        category=topic,
        count=len(items),
        items=items,
        note=(
            "Vídeos reais do YouTube em português. Avaliação preliminar não realizada: "
            "ainda não há análise de IA nem nota de qualidade."
        ),
    )
