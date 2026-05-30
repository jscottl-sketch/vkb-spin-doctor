"""
storm_bridge.py — STORM (Selective Targeted Output Remove Merge) bridge.
Provides StormBridge class for ingesting and querying the STORM feed.
Used by: hisav_detective.py, aafl_wccs.py, any future agent.
"""

import datetime
import json
import urllib.request
import urllib.parse

MCC_HOST = "http://127.0.0.1:8080"


class StormBridge:
    def ingest(self, source: str, category: str, data_dict: dict) -> bool:
        payload = {
            "source": source,
            "category": category,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "resolved": False,
            **data_dict,
        }
        try:
            body = json.dumps(payload).encode()
            req = urllib.request.Request(
                f"{MCC_HOST}/api/storm/ingest",
                data=body,
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=5)
            return True
        except Exception:
            return False

    def get_feed(self, severity: str = None, limit: int = 50) -> list:
        try:
            params = {"limit": str(limit)}
            if severity:
                params["severity"] = severity
            qs = urllib.parse.urlencode(params)
            resp = urllib.request.urlopen(f"{MCC_HOST}/api/storm/feed?{qs}", timeout=5)
            data = json.loads(resp.read())
            return data.get("entries", [])
        except Exception:
            return []

    def get_summary(self) -> dict:
        try:
            resp = urllib.request.urlopen(f"{MCC_HOST}/api/storm/summary", timeout=5)
            return json.loads(resp.read())
        except Exception:
            return {}
