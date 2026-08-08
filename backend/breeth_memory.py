import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()


class BreethMemory:
    def __init__(self) -> None:
        self.api_key = os.getenv("BREETH_API_KEY")
        self.base_url = os.getenv(
            "BREETH_BASE_URL",
            "https://api.thebreeth.com",
        ).rstrip("/")

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise RuntimeError("BREETH_API_KEY is not configured")

        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def add_episode(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        """Store an interview conversation in Breeth."""
        if not self.enabled:
            return {"enabled": False}

        response = requests.post(
            f"{self.base_url}/v1/episodes",
            headers=self._headers(),
            json={
                "content": "\n".join(
                    f"{message['role']}: {message['content']}"
                    for message in messages
                )
            },
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    def search_memory(
        self,
        query: str,
        limit: int = 5,
    ) -> dict[str, Any]:
        """Retrieve relevant interview memories from Breeth."""
        if not self.enabled:
            return {"enabled": False, "results": []}

        response = requests.post(
            f"{self.base_url}/v1/search",
            headers=self._headers(),
            json={
                "query": query,
                "limit": limit,
            },
            timeout=15,
        )
        response.raise_for_status()
        return response.json()