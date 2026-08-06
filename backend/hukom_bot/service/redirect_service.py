from __future__ import annotations
from backend.hukom_bot.core.settings import settings


class RedirectService:
    _instance: RedirectService | None = None

    def __init__(self):
        self.base_page_url = settings.BASE_PAGE_URL
        self.base_api_url = settings.BASE_API_URL

    @classmethod
    def initialize(cls) -> RedirectService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def get_instance(cls) -> RedirectService:
        if cls._instance is None:
            return RuntimeError("Redirect service is not initialized")
        return cls._instance

    def get_redirect_url(self, path: str, payload: dict | None = None) -> str:
        """
        Returns the full redirect URL based on the base page URL and the provided path.
        If a payload is provided, it will be converted to query parameters and appended to the URL
        """
        path = self._remove_slashes(path)

        if payload:
            return f"{self.base_page_url}/{path}?{self._dict_to_query_string(payload)}"
        return f"{self.base_page_url}/{path}"

    def get_api_url(self, path: str, payload: dict | None = None) -> str:
        """
        Returns the full API URL based on the base API URL and the provided path.
        If a payload is provided, it will be converted to query parameters and appended to the URL
        """
        path = self._remove_slashes(path)

        if payload:
            return f"{self.base_api_url}/{path}?{self._dict_to_query_string(payload)}"
        return f"{self.base_api_url}/{path}"

    def _remove_slashes(self, url: str) -> str:
        """
        Removes the leading and trailing slashes from a URL if they exist.
        """
        # Remove leading slash if it exists
        url = url[1:] if url.startswith("/") else url
        # Remove trailing slash if it exists
        return url[:-1] if url.endswith("/") else url

    def _dict_to_query_string(self, payload: dict) -> str:
        """
        Converts a dictionary to a query string.
        """
        return "&".join(f"{key}={value}" for key, value in payload.items())


redirect_service = RedirectService.initialize()
