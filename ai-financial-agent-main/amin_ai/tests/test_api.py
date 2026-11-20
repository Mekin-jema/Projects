from tavily.errors import ForbiddenError

from app.core.tools import search_tool


def test_search_tool_reports_missing_api_key(monkeypatch):
	monkeypatch.delenv("TAVILY_API_KEY", raising=False)

	result = search_tool.invoke({"query": "latest AI headlines"})

	assert "missing" in str(result).lower()


def test_search_tool_handles_forbidden_error(monkeypatch):
	monkeypatch.setenv("TAVILY_API_KEY", "bad-key")

	import tavily

	def fake_search(self, *args, **kwargs):
		raise ForbiddenError("403 forbidden")

	monkeypatch.setattr(tavily.TavilyClient, "search", fake_search)

	result = search_tool.invoke({"query": "latest AI headlines"})

	assert "invalid" in str(result).lower() or "blocked" in str(result).lower()
