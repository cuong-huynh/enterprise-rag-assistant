"""Low-level Odoo XML-RPC client shared by ERP query and document sync."""

from __future__ import annotations

import xmlrpc.client
from typing import Any
from urllib.parse import urljoin

from assistant.core.config import settings


class OdooRpcClient:
    """Authenticate and call ``execute_kw`` on Odoo models."""

    def __init__(
        self,
        *,
        url: str | None = None,
        db: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        self._url = (url or settings.odoo_url).rstrip("/")
        self._db = db or settings.odoo_db
        self._username = username or settings.odoo_username
        self._password = password or settings.odoo_password
        self._uid: int | None = None
        self._object_proxy: xmlrpc.client.ServerProxy | None = None
        self._common_proxy: xmlrpc.client.ServerProxy | None = None

    @property
    def db(self) -> str:
        return self._db

    def _object_proxy_client(self) -> xmlrpc.client.ServerProxy:
        if self._object_proxy is None:
            endpoint = urljoin(f"{self._url}/", "xmlrpc/2/object")
            self._object_proxy = xmlrpc.client.ServerProxy(endpoint, allow_none=True)
        return self._object_proxy

    def _common_proxy_client(self) -> xmlrpc.client.ServerProxy:
        if self._common_proxy is None:
            endpoint = urljoin(f"{self._url}/", "xmlrpc/2/common")
            self._common_proxy = xmlrpc.client.ServerProxy(endpoint, allow_none=True)
        return self._common_proxy

    def authenticate(self) -> int:
        if self._uid is not None:
            return self._uid
        uid = self._common_proxy_client().authenticate(
            self._db,
            self._username,
            self._password,
            {},
        )
        if not uid:
            raise PermissionError(
                f"Odoo authentication failed for user {self._username!r} on db {self._db!r}."
            )
        self._uid = int(uid)
        return self._uid

    def execute_kw(
        self,
        model: str,
        method: str,
        args: list[Any] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> Any:
        uid = self.authenticate()
        try:
            return self._object_proxy_client().execute_kw(
                self._db,
                uid,
                self._password,
                model,
                method,
                args or [],
                kwargs or {},
            )
        except xmlrpc.client.Fault as exc:
            raise RuntimeError(f"Odoo {model}.{method} failed: {exc.faultString}") from exc

    def search_read(
        self,
        model: str,
        domain: list[Any],
        *,
        fields: list[str],
        limit: int = 100,
        order: str | None = None,
    ) -> list[dict[str, Any]]:
        kwargs: dict[str, Any] = {"fields": fields, "limit": limit}
        if order:
            kwargs["order"] = order
        rows = self.execute_kw(model, "search_read", [domain], kwargs)
        if not isinstance(rows, list):
            raise RuntimeError(f"Unexpected Odoo response type: {type(rows)!r}")
        return rows
