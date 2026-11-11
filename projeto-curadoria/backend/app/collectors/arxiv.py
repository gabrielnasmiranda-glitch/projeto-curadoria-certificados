"""Coletor da API pública do arXiv (https://info.arxiv.org/help/api/).

Respeita as orientações do arXiv: poucas requisições, User-Agent identificado e
resultados limitados. O parse é separado da requisição para facilitar testes.
"""

import re
from datetime import datetime, timezone

import feedparser
import httpx

from app.core.http import build_verify
from app.schemas.content import ContentPreview

ARXIV_API_URL = "https://export.arxiv.org/api/query"
USER_AGENT = "curadoria-mvp/0.1 (projeto de curadoria de conhecimento)"
REQUEST_TIMEOUT_SECONDS = 15.0

# Categorias permitidas (lista fechada: evita injeção na query de busca)
ALLOWED_CATEGORIES: dict[str, str] = {
    "cs.AI": "Inteligência artificial",
    "cs.LG": "Aprendizado de máquina",
    "cs.CL": "Linguagem natural",
    "cs.SE": "Engenharia de software",
    "q-fin.GN": "Finanças (geral)",
    "econ.GN": "Economia (geral)",
    "physics.hist-ph": "História e filosofia da física",
    "q-bio.NC": "Neurociência",
}


class CollectorError(Exception):
    """Falha ao coletar de uma fonte externa."""


def _normalize_text(value: str | None) -> str | None:
    if not value:
        return None
    return re.sub(r"\s+", " ", value).strip() or None


def _arxiv_id(entry_id: str) -> str:
    # http://arxiv.org/abs/2401.01234v2  ->  2401.01234 (sem a versão)
    raw = entry_id.rsplit("/abs/", 1)[-1]
    return re.sub(r"v\d+$", "", raw)


def parse_arxiv_feed(xml_text: str) -> list[ContentPreview]:
    parsed = feedparser.parse(xml_text)
    items: list[ContentPreview] = []
    for entry in parsed.entries:
        entry_id = entry.get("id")
        title = _normalize_text(entry.get("title"))
        if not entry_id or not title:
            continue  # entrada inválida: ignora em vez de inventar campos

        published_at = None
        if entry.get("published_parsed"):
            published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

        items.append(
            ContentPreview(
                external_id=_arxiv_id(entry_id),
                source="arXiv",
                title=title,
                summary=_normalize_text(entry.get("summary")),
                authors=[a.get("name", "") for a in entry.get("authors", []) if a.get("name")],
                categories=[t.get("term", "") for t in entry.get("tags", []) if t.get("term")],
                published_at=published_at,
                url=entry.get("link") or entry_id,
            )
        )
    return items


def fetch_arxiv(category: str, max_results: int = 10) -> list[ContentPreview]:
    if category not in ALLOWED_CATEGORIES:
        raise ValueError(f"Categoria não permitida: {category}")

    params = {
        "search_query": f"cat:{category}",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "start": 0,
        "max_results": max_results,
    }
    try:
        response = httpx.get(
            ARXIV_API_URL,
            params=params,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT_SECONDS,
            follow_redirects=True,
            verify=build_verify(),
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise CollectorError(f"Não foi possível consultar o arXiv: {exc}") from exc

    return parse_arxiv_feed(response.text)
