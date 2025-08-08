"""Utilities for importing dashboards into Kibana/Wazuh Dash."""
from __future__ import annotations

from pathlib import Path
import os

import requests

DASHBOARDS_DIR = Path(__file__).resolve().parent.parent / "dashboards"


def import_dashboards(kibana_url: str | None = None) -> None:
    """Import all NDJSON dashboards using Kibana saved objects API."""
    url = kibana_url or os.environ.get("KIBANA_URL", "http://soc01:5601")
    for ndjson in DASHBOARDS_DIR.glob("*.ndjson"):
        with ndjson.open("rb") as fh:
            response = requests.post(
                f"{url}/api/saved_objects/_import",
                params={"overwrite": "true"},
                files={"file": fh},
                headers={"kbn-xsrf": "true"},
                timeout=30,
            )
        response.raise_for_status()
