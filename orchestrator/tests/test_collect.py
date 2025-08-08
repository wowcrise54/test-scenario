from __future__ import annotations

from pathlib import Path
import zipfile
from typer.testing import CliRunner
import pytest
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from orchestrator import cli, collect as collector


def test_collect_creates_zip(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    state_dir = tmp_path / "state"
    (state_dir / "evtx" / "WIN01").mkdir(parents=True)
    (state_dir / "evtx" / "WIN01" / "Security.evtx").write_text("sec")
    (state_dir / "evtx" / "WIN01" / "Sysmon.evtx").write_text("sys")
    (state_dir / "winlogbeat").mkdir()
    (state_dir / "winlogbeat" / "index.ndjson").write_text("{}\n")
    (state_dir / "suricata").mkdir()
    (state_dir / "suricata" / "alerts.pcap").write_bytes(b"pcap")

    monkeypatch.setattr(cli, "STATE_DIR", state_dir)
    monkeypatch.setattr(collector, "STATE_DIR", state_dir)

    runner = CliRunner()
    artifacts_dir = tmp_path / "artifacts"
    result = runner.invoke(cli.app, ["collect", "--out", str(artifacts_dir)])
    assert result.exit_code == 0

    zips = list(artifacts_dir.glob("*.zip"))
    assert len(zips) == 1
    zip_path = zips[0]
    run_id = zip_path.stem
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = set(zf.namelist())
    expected = {
        f"{run_id}/evtx/WIN01/Security.evtx",
        f"{run_id}/evtx/WIN01/Sysmon.evtx",
        f"{run_id}/winlogbeat/index.ndjson",
        f"{run_id}/suricata/alerts.pcap",
    }
    assert expected.issubset(names)
