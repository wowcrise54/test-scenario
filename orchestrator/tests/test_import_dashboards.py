from __future__ import annotations

from pathlib import Path
import pytest
import requests

from orchestrator import import_dashboards as imp


def test_import_dashboards(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    sample = tmp_path / "sample.ndjson"
    sample.write_text("{}\n")

    calls: list[str] = []

    def fake_post(url: str, **kwargs: object) -> object:
        calls.append(url)

        class Resp:
            def raise_for_status(self) -> None:  # pragma: no cover
                pass

        return Resp()

    monkeypatch.setattr(imp, "DASHBOARDS_DIR", tmp_path)
    monkeypatch.setattr(requests, "post", fake_post)

    imp.import_dashboards("http://example.com")

    assert calls == ["http://example.com/api/saved_objects/_import"]
