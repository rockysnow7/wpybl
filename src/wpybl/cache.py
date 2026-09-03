from datetime import datetime, timedelta, UTC
from pydantic import ConfigDict, BaseModel
from tqdm import tqdm

import json
import os
import requests
import time


_WPYBL_DATA_DIR = ".wpybl_data"
if not os.path.exists(_WPYBL_DATA_DIR):
    os.makedirs(_WPYBL_DATA_DIR)

_WEB_CACHE_FILE = f"{_WPYBL_DATA_DIR}/web_cache.json"


class _WebCache(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    kv: dict[str, str] = {}  # url -> html
    expires_at: dict[str, datetime | None] = {}  # url -> datetime | never

    def __getitem__(self, url: str) -> str | None:
        if url not in self.kv:
            return None
        if (
            self.expires_at.get(url) is not None
            and datetime.now(UTC) >= self.expires_at[url]  # type: ignore
        ):
            del self.kv[url]
            del self.expires_at[url]
            self.__save()
        return self.kv.get(url)

    def cache(self, url: str, html: str, *, cache_forever: bool = False) -> None:
        if cache_forever:
            expires_at = None
        else:
            expires_at = (datetime.now(UTC) + timedelta(days=1)).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )  # midnight tonight

        self.kv[url] = html
        self.expires_at[url] = expires_at
        self.__save()

    def __save(self) -> None:
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
        self.__save()


_web_cache = _WebCache()
_web_cache.load()


def clear_cache() -> None:
    """Clears the web cache."""

    _web_cache.clear()


def _get_url(
    url: str,
    *,
    cache_forever: bool = False,
    return_hit_bool: bool = False,
) -> str | tuple[str, bool]:
    """
    Downloads the text from a URL and caches it, or returns the cached version if it is available and hasn't expired.

    Args:
        url (str): The URL to download.
        cache_forever (bool, optional): If True, the cached version will never expire. Defaults to False.
        return_hit_bool (bool, optional): If True, the function will return a tuple containing the text and a boolean indicating whether the text was retrieved from the cache. Defaults to False.
    """

    text = _web_cache[url]
    if text is None:
        response = requests.get(url)
        text = response.text
        _web_cache.cache(url, text, cache_forever=cache_forever)

        if return_hit_bool:
            return text, False
        return text

    if return_hit_bool:
        return text, True
    return text


def _get_urls(
    urls: list[str],
    *,
    cache_forever: bool | list[bool] = False,
    timeout: float = 1.0,
    tqdm_desc: str | None = None,
) -> list[str]:
    """
    Downloads the texts of multiple URLs and caches them, or returns the cached versions if they are available and haven't expired.

    Args:
        urls (list[str]): The URLs to download.
        cache_forever (bool | list[bool], optional): If True, the cached versions will never expire. If a list, the i-th element specifies whether the i-th URL should be cached forever. Defaults to False.
        timeout (float, optional): The amount of time, in seconds, to wait between requests. Defaults to 1.0.
        tqdm_desc (str, optional): The text to display in the progress bar. If None, no progress bar will be displayed. Defaults to None.
    """

    if not isinstance(cache_forever, list):
        cache_forever = [cache_forever] * len(urls)

    zipped = list(zip(urls, cache_forever))  # type: ignore
    if tqdm_desc is not None:
        zipped = tqdm(zipped, desc=tqdm_desc)

    texts = []
    for url, forever in zipped:
        text, hit = _get_url(url, cache_forever=forever, return_hit_bool=True)
        texts.append(text)
        if not hit:
            time.sleep(timeout)
    return texts
