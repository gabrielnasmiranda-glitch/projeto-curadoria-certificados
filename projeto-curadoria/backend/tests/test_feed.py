import pytest
from fastapi.testclient import TestClient

from app.api import feed as feed_module
from app.collectors import arxiv
from app.collectors.arxiv import CollectorError, parse_arxiv_feed
from app.main import app

client = TestClient(app)

# Amostra no formato Atom devolvido pela API do arXiv (usada apenas nos testes do parser).
SAMPLE_ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2401.01234v2</id>
    <updated>2024-01-03T10:00:00Z</updated>
    <published>2024-01-02T09:30:00Z</published>
    <title>Um   título
      com quebras</title>
    <summary>  Resumo   do artigo.  </summary>
    <author><name>Ana Silva</name></author>
    <author><name>Bruno Costa</name></author>
    <link href="http://arxiv.org/abs/2401.01234v2" rel="alternate" type="text/html"/>
    <category term="cs.AI" scheme="http://arxiv.org/schemas/atom"/>
    <category term="cs.LG" scheme="http://arxiv.org/schemas/atom"/>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2401.99999v1</id>
    <title></title>
  </entry>
</feed>
"""


@pytest.fixture(autouse=True)
def clear_cache():
    feed_module._cache.clear()
    yield
    feed_module._cache.clear()


def test_parse_extracts_fields_and_normalizes_text():
    items = parse_arxiv_feed(SAMPLE_ATOM)
    assert len(items) == 1  # a entrada sem título é descartada, não preenchida
    item = items[0]
    assert item.external_id == "2401.01234"  # sem o sufixo de versão
    assert item.title == "Um título com quebras"
    assert item.summary == "Resumo do artigo."
    assert item.authors == ["Ana Silva", "Bruno Costa"]
    assert item.categories == ["cs.AI", "cs.LG"]
    assert item.published_at is not None and item.published_at.year == 2024
    assert item.source == "arXiv"
    assert item.url.startswith("http")


def test_parse_empty_feed_returns_empty_list():
    assert parse_arxiv_feed("<feed xmlns='http://www.w3.org/2005/Atom'></feed>") == []


def test_fetch_rejects_unknown_category():
    with pytest.raises(ValueError):
        arxiv.fetch_arxiv("cs.AI OR all:malicioso")


def test_endpoint_returns_items(monkeypatch):
    items = parse_arxiv_feed(SAMPLE_ATOM)
    monkeypatch.setattr(feed_module, "fetch_arxiv", lambda category, limit: items)
    response = client.get("/api/feed/preview?category=cs.AI&limit=5")
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    assert body["evaluated"] is False
    assert body["items"][0]["title"] == "Um título com quebras"


def test_endpoint_rejects_invalid_category():
    response = client.get("/api/feed/preview?category=xxx")
    assert response.status_code == 422


def test_endpoint_rejects_out_of_range_limit():
    assert client.get("/api/feed/preview?limit=0").status_code == 422
    assert client.get("/api/feed/preview?limit=999").status_code == 422


def test_endpoint_returns_502_when_source_fails(monkeypatch):
    def boom(category, limit):
        raise CollectorError("falha simulada")

    monkeypatch.setattr(feed_module, "fetch_arxiv", boom)
    response = client.get("/api/feed/preview?category=cs.AI")
    assert response.status_code == 502


def test_endpoint_uses_cache(monkeypatch):
    calls = {"n": 0}

    def fake(category, limit):
        calls["n"] += 1
        return []

    monkeypatch.setattr(feed_module, "fetch_arxiv", fake)
    client.get("/api/feed/preview?category=cs.AI&limit=5")
    client.get("/api/feed/preview?category=cs.AI&limit=5")
    assert calls["n"] == 1


def test_categories_endpoint():
    body = client.get("/api/feed/categories").json()
    assert "cs.AI" in body
