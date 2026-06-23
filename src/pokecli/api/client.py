import httpx

from pokecli.config import POKEAPI_BASE_URL


class PokeAPIClient:
    def __init__(self, base_url: str = POKEAPI_BASE_URL, timeout: float = 10.0):
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    def get_resource(self, resource: str, identifier: str | int) -> dict:
        response = self._client.get(f"/{resource}/{identifier}/")
        response.raise_for_status()
        return response.json()

    def list_resource(self, resource: str, limit: int, offset: int) -> dict:
        response = self._client.get(
            f"/{resource}/", params={"limit": limit, "offset": offset}
        )
        response.raise_for_status()
        return response.json()

    def get_resource_by_url(self, url: str) -> dict:
        response = self._client.get(url)
        response.raise_for_status()
        return response.json()

    def get_subresource(
        self, resource: str, identifier: str | int, sub: str
    ) -> list | dict:
        """Fetch a nested endpoint like /pokemon/{id}/encounters/."""
        response = self._client.get(f"/{resource}/{identifier}/{sub}/")
        response.raise_for_status()
        return response.json()

    def download_bytes(self, url: str) -> bytes:
        response = self._client.get(url, follow_redirects=True, timeout=30.0)
        response.raise_for_status()
        return response.content

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "PokeAPIClient":
        return self

    def __exit__(self, *_) -> None:
        self.close()
