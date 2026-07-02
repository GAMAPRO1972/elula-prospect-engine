"""
integrations/ghl/api.py

Production GoHighLevel API client.
"""

from __future__ import annotations

import time
from typing import Any

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import settings
from integrations.ghl.logger import (
    log_exception,
    log_request,
    log_response,
)

_TRANSIENT = {429, 500, 502, 503, 504}


class GHLAPIError(Exception):
    """Raised when the GoHighLevel API returns an unrecoverable error."""


class GHLClient:
    def __init__(self) -> None:
        self.base_url = settings.ghl_base_url.rstrip("/")
        self.session = requests.Session()

        retry = Retry(
            total=settings.max_retries,
            backoff_factor=settings.retry_backoff,
            status_forcelist=list(_TRANSIENT),
            allowed_methods=frozenset(["GET", "POST", "PUT", "DELETE"]),
            raise_on_status=False,
        )

        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.session.headers.update(
            {
                "Authorization": f"Bearer {settings.ghl_api_key}",
                "Version": settings.ghl_api_version,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        timeout = (
            settings.connect_timeout,
            settings.request_timeout,
        )

        log_request(method, endpoint)
        started = time.perf_counter()

        try:
            response: Response = self.session.request(
                method=method,
                url=url,
                timeout=timeout,
                **kwargs,
            )
        except requests.RequestException as exc:
            log_exception("HTTP request failed", exc)
            raise GHLAPIError(str(exc)) from exc

        elapsed = int((time.perf_counter() - started) * 1000)
        log_response(method, endpoint, response.status_code, elapsed)

        if response.status_code >= 400:
            try:
                detail = response.json()
            except Exception:
                detail = response.text

            raise GHLAPIError(
                f"{response.status_code}: {detail}"
            )

        if response.content:
            try:
                return response.json()
            except ValueError:
                return response.text

        return None

    def get(self, endpoint: str, params: dict | None = None) -> Any:
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, payload: dict | None = None) -> Any:
        return self._request("POST", endpoint, json=payload)

    def put(self, endpoint: str, payload: dict | None = None) -> Any:
        return self._request("PUT", endpoint, json=payload)

    def delete(self, endpoint: str) -> Any:
        return self._request("DELETE", endpoint)


ghl = GHLClient()
