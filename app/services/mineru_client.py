from typing import Any
import httpx


class MinerUClient:
    """HTTP client for MinerU instances."""

    def __init__(self, base_url: str, timeout: int = 300):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def submit_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Submit a task to MinerU instance."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/pdf_parse",
                json=payload
            )
            response.raise_for_status()
            return response.json()

    async def health_check(self, timeout: int = 10) -> bool:
        """Check if instance is healthy."""
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception:
            return False
