from datetime import datetime, timedelta, UTC
from pydantic import ConfigDict, BaseModel

import json
import os
import requests


_WPYBL_DATA_DIR = ".wpybl_data"
if not os.path.exists(_WPYBL_DATA_DIR):
    os.makedirs(_WPYBL_DATA_DIR)

_WEB_CACHE_FILE = f"{_WPYBL_DATA_DIR}/web_cache.json"


class _WebCache(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    kv: dict[str, str] = {}  # url -> html
    expires_at: dict[str, datetime] = {}  # url -> datetime

    def __getitem__(self, url: str) -> str | None:
        if url not in self.kv:
            return None
        if datetime.now(UTC) >= self.expires_at[url]:
            del self.kv[url]
            del self.expires_at[url]
            self.save()
        return self.kv.get(url)

    def __setitem__(self, url: str, html: str) -> None:
        self.kv[url] = html
        expires_at = (datetime.now(UTC) + timedelta(days=1)).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )  # midnight tonight
        self.expires_at[url] = expires_at
        self.save()

    def save(self) -> None:
        model = self.model_dump(mode="json")
        with open(_WEB_CACHE_FILE, "w") as f:
            json.dump(model, f, indent=4)

    def load(self) -> None:
        if not os.path.exists(_WEB_CACHE_FILE):
            return

        with open(_WEB_CACHE_FILE) as f:
            data = json.load(f)
        new = self.model_validate(data)
        self.kv = new.kv
        self.expires_at = new.expires_at

    def clear(self) -> None:
        self.kv = {}
        self.expires_at = {}
        self.save()


_web_cache = _WebCache()
_web_cache.load()


def clear_cache() -> None:
    """Clears the web cache."""

    _web_cache.clear()


def _get_url(url: str) -> str:
    """Downloads the text from a URL and caches it for the rest of the day, or returns the cached version if it is available and hasn't expired."""

    text = _web_cache[url]
    if text is None:
        response = requests.get(url)
        text = response.text
        _web_cache[url] = text
    return text
