"""共用的 HTTP GET：帶瀏覽器 User-Agent，失敗時丟出例外。"""
import requests

from .. import config


def _get(url: str, **kwargs) -> requests.Response:
    headers = {"User-Agent": config.USER_AGENT, **kwargs.pop("headers", {})}
    resp = requests.get(url, headers=headers, timeout=30, **kwargs)
    resp.raise_for_status()
    return resp
