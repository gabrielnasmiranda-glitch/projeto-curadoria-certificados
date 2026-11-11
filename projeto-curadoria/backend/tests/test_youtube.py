import httpx
import pytest
from fastapi.testclient import TestClient

from app.api import feed as feed_module
from app.collectors import youtube
from app.collectors.arxiv import CollectorError
from app.collectors.youtube import MissingApiKeyError, fetch_youtube, parse_search_items
from app.core.config import Settings
from app.main import app

client = TestClient(app)

SEARCH_SAMPLE = {
    "items": [
        {
            "id": {"kind": "youtube#video", "videoId": "abc123"},
            "snippet": {
                "title": "Aula de IA &amp; ética &#39;básica&#39;",
                "description": "Descrição da aula",
                "channelTitle": "Canal Exemplo",
                "publishedAt": "2025-03-01T12:00:00Z",
                "thumbnails": {"default": {"url": "http://t/d.jpg"}, "high": {"url": "http://t/h.jpg"}},
            },
        },
        {"id": {"kind": "youtube#channel", "channelId": "xyz"}, "snippet": {"title": "Canal"}},
        {"id": {"videoId": "semtitulo"}, "snippet": {"title": ""}},
    ]
}


@pytest.fixture(autouse=True)
def clear_cache():
    feed_module._cache.clear()
    yield
    feed_module._cache.clear()


def test_parse_search_items_unescapes_and_skips_invalid():
    items = parse_search_items(SEARCH_SAMPLE, {"abc123": 4200})
    assert len(items) == 1
    item = items[0]
    assert item.title == "Aula de IA & ética 'básica'"
    assert item.authors == ["Canal Exemplo"]
    assert item.url == "https://www.youtube.com/watch?v=abc123"
    assert item.thumbnail_url == "http://t/h.jpg"
    assert item.view_count == 4200
    assert item.source == "YouTube"


def test_missing_key_raises_clear_error():
    with pytest.raises(MissingApiKeyError):
        fetch_youtube("", "ia")


def test_unknown_topic_rejected():
    with pytest.raises(ValueError):
        fetch_youtube("chave", "hackear")


def test_fetch_combines_search_and_stats(monkeypatch):
    calls = []

    def fake_get_json(url, params):
        calls.append((url, params))
        if url == youtube.SEARCH_URL:
            return SEARCH_SAMPLE
        return {"items": [{"id": "abc123", "statistics": {"viewCount": "99"}}]}

    monkeypatch.setattr(youtube, "_get_json", fake_get_json)
    items = fetch_youtube("k", "ia", 5)
    assert items[0].view_count == 99
    search_params = calls[0][1]
    assert search_params["relevanceLanguage"] == "pt"
    assert search_params["regionCode"] == "BR"
    assert search_params["type"] == "video"


def test_http_error_message_does_not_leak_api_key(monkeypatch):
    def boom(url, params, timeout, **kwargs):
        raise httpx.ConnectError("falha em https://x?key=SEGREDO123")

    monkeypatch.setattr(youtube.httpx, "get", boom)
    with pytest.raises(CollectorError) as info:
        fetch_youtube("SEGREDO123", "ia")
    assert "SEGREDO123" not in str(info.value)


def test_api_error_status_reports_reason_without_key(monkeypatch):
    def fake_get(url, params, timeout, **kwargs):
        return httpx.Response(
            403,
            json={"error": {"errors": [{"reason": "quotaExceeded"}], "message": "m"}},
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr(youtube.httpx, "get", fake_get)
    with pytest.raises(CollectorError) as info:
        fetch_youtube("SEGREDO123", "ia")
    message = str(info.value)
    assert "403" in message and "quotaExceeded" in message
    assert "SEGREDO123" not in message


def test_endpoint_503_without_key(monkeypatch):
    monkeypatch.setattr(feed_module, "get_settings", lambda: Settings(youtube_api_key=""))
    response = client.get("/api/feed/youtube?topic=ia")
    assert response.status_code == 503
    assert "YOUTUBE_API_KEY" in response.json()["detail"]


def test_endpoint_returns_videos(monkeypatch):
    monkeypatch.setattr(feed_module, "get_settings", lambda: Settings(youtube_api_key="k"))
    monkeypatch.setattr(
        feed_module,
        "fetch_youtube",
        lambda key, topic, limit: parse_search_items(SEARCH_SAMPLE, {}),
    )
    body = client.get("/api/feed/youtube?topic=filosofia&limit=5").json()
    assert body["count"] == 1
    assert body["items"][0]["source"] == "YouTube"
    assert body["evaluated"] is False


def test_endpoint_validation_and_topics():
    assert client.get("/api/feed/youtube?topic=xxx").status_code == 422
    assert client.get("/api/feed/youtube?limit=0").status_code == 422
    topics = client.get("/api/feed/youtube/topics").json()
    assert topics["ia"] == "Inteligência artificial"
    assert len(topics) == 13
