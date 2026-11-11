"""Coletor do YouTube via YouTube Data API v3 (oficial).

- search.list (100 unidades de cota por chamada) descobre vídeos em português.
- videos.list (1 unidade) traz as estatísticas públicas permitidas.
- Transcrições NÃO são coletadas: a API não as fornece automaticamente.
- A chave de API nunca aparece em mensagens de erro nem em logs.
"""

import html
from datetime import datetime

import httpx

from app.collectors.arxiv import CollectorError
from app.core.http import build_verify
from app.schemas.content import ContentPreview

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
REQUEST_TIMEOUT_SECONDS = 15.0

# Tópicos em português (lista fechada). Cada um vira uma consulta de busca.
TOPICS: dict[str, tuple[str, str]] = {
    "tecnologia": ("Tecnologia", "tecnologia explicada"),
    "programacao": ("Programação", "programação aula completa"),
    "ia": ("Inteligência artificial", "inteligência artificial explicada"),
    "ciencia": ("Ciência", "divulgação científica"),
    "filosofia": ("Filosofia", "filosofia aula"),
    "psicologia": ("Psicologia", "psicologia aula"),
    "historia": ("História", "história documentário"),
    "economia": ("Economia", "economia explicada"),
    "financas": ("Finanças", "educação financeira investimentos"),
    "empreendedorismo": ("Empreendedorismo", "empreendedorismo negócios"),
    "musica": ("Música", "teoria musical aula"),
    "comunicacao": ("Comunicação", "comunicação oratória"),
    "desenvolvimento-pessoal": ("Desenvolvimento pessoal", "desenvolvimento pessoal"),
}


class MissingApiKeyError(CollectorError):
    """A YOUTUBE_API_KEY não está configurada."""


def _get_json(url: str, params: dict) -> dict:
    try:
        response = httpx.get(
            url, params=params, timeout=REQUEST_TIMEOUT_SECONDS, verify=build_verify()
        )
    except httpx.HTTPError as exc:
        # Não inclui str(exc): a URL da requisição contém a chave.
        raise CollectorError(
            f"Não foi possível conectar ao YouTube ({type(exc).__name__})."
        ) from None

    if response.status_code >= 400:
        reason = ""
        try:
            error = response.json().get("error", {})
            reason = error.get("errors", [{}])[0].get("reason") or error.get("message", "")
        except ValueError:
            pass
        raise CollectorError(
            f"A API do YouTube respondeu com erro {response.status_code}"
            + (f" ({reason})" if reason else "")
            + "."
        )
    return response.json()


def _pick_thumbnail(thumbnails: dict) -> str | None:
    for size in ("high", "medium", "default"):
        url = thumbnails.get(size, {}).get("url")
        if url:
            return url
    return None


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def parse_search_items(search_json: dict, stats: dict[str, int]) -> list[ContentPreview]:
    items: list[ContentPreview] = []
    for entry in search_json.get("items", []):
        video_id = entry.get("id", {}).get("videoId")
        snippet = entry.get("snippet", {})
        title = html.unescape(snippet.get("title", "")).strip()
        if not video_id or not title:
            continue  # entrada inválida: ignora em vez de inventar campos

        description = html.unescape(snippet.get("description", "")).strip() or None
        channel = html.unescape(snippet.get("channelTitle", "")).strip()
        items.append(
            ContentPreview(
                external_id=video_id,
                source="YouTube",
                title=title,
                summary=description,
                authors=[channel] if channel else [],
                published_at=_parse_datetime(snippet.get("publishedAt")),
                url=f"https://www.youtube.com/watch?v={video_id}",
                thumbnail_url=_pick_thumbnail(snippet.get("thumbnails", {})),
                view_count=stats.get(video_id),
            )
        )
    return items


def fetch_youtube(api_key: str, topic: str, max_results: int = 10) -> list[ContentPreview]:
    if not api_key:
        raise MissingApiKeyError(
            "YOUTUBE_API_KEY não configurada. Defina a chave no arquivo .env e reinicie o backend."
        )
    if topic not in TOPICS:
        raise ValueError(f"Tópico não permitido: {topic}")

    search_json = _get_json(
        SEARCH_URL,
        {
            "part": "snippet",
            "q": TOPICS[topic][1],
            "type": "video",
            "relevanceLanguage": "pt",
            "regionCode": "BR",
            "safeSearch": "moderate",
            "videoDuration": "medium",  # 4 a 20 minutos; evita clipes muito curtos
            "maxResults": max_results,
            "key": api_key,
        },
    )

    ids = [
        e["id"]["videoId"]
        for e in search_json.get("items", [])
        if e.get("id", {}).get("videoId")
    ]
    stats: dict[str, int] = {}
    if ids:
        videos_json = _get_json(
            VIDEOS_URL, {"part": "statistics", "id": ",".join(ids), "key": api_key}
        )
        for video in videos_json.get("items", []):
            count = video.get("statistics", {}).get("viewCount")
            if count is not None and str(count).isdigit():
                stats[video["id"]] = int(count)

    return parse_search_items(search_json, stats)
