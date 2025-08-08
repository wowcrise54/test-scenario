from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import shutil
import zipfile

STATE_DIR = Path("state")


def _collect_evtx(target_dir: Path) -> None:
    src_root = STATE_DIR / "evtx"
    if not src_root.exists():
        return
    for host_dir in src_root.iterdir():
        if host_dir.is_dir():
            dest = target_dir / "evtx" / host_dir.name
            dest.mkdir(parents=True, exist_ok=True)
            for name in ["Security.evtx", "Sysmon.evtx"]:
                src = host_dir / name
                if src.exists():
                    shutil.copy2(src, dest / name)


def _collect_winlogbeat(target_dir: Path) -> None:
    src_root = STATE_DIR / "winlogbeat"
    if not src_root.exists():
        return
    dest_root = target_dir / "winlogbeat"
    dest_root.mkdir(parents=True, exist_ok=True)
    for file in src_root.glob("*.ndjson"):
        shutil.copy2(file, dest_root / file.name)


def _collect_suricata(target_dir: Path) -> None:
    src_root = STATE_DIR / "suricata"
    if not src_root.exists():
        return
    dest_root = target_dir / "suricata"
    dest_root.mkdir(parents=True, exist_ok=True)
    for file in src_root.glob("*.pcap"):
        shutil.copy2(file, dest_root / file.name)


def collect_artifacts(out: Path) -> Path:
    """Collect artifacts into a timestamped zip archive.

    The function searches under ``STATE_DIR`` for prepared artifact files:
    ``evtx/<host>/Security.evtx`` and ``Sysmon.evtx``, ``winlogbeat/*.ndjson``
    and ``suricata/*.pcap``. These files are copied into a directory
    ``out/<run_id>`` and zipped to ``out/<run_id>.zip``.
    Returns the path to the created zip archive.
    """

    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = out / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    _collect_evtx(run_dir)
    _collect_winlogbeat(run_dir)
    _collect_suricata(run_dir)

    zip_path = out / f"{run_id}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in run_dir.rglob("*"):
            if file.is_file():
                zf.write(file, arcname=file.relative_to(out))
    return zip_path
