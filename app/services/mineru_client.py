from typing import Any
import httpx


class MinerUClient:
    """HTTP client for MinerU instances."""

    def __init__(self, base_url: str, timeout: int = 300):
        self.base_url = base_url.rstrip("/")
        # Add extra buffer to httpx timeout so asyncio.wait_for fires first
        self.timeout = timeout + 10

    async def submit_task(self, payload: dict[str, Any], instance_backend: str | None = None) -> dict[str, Any]:
        """Submit a task to MinerU instance.

        Args:
            payload: The task payload to send.
            instance_backend: The backend configured on the target instance.
                If payload backend is 'auto' or missing, it will be replaced
                with the instance's backend value.
        """
        # Backend conversion logic
        payload_backend = payload.get("backend")
        if payload_backend == "auto" or not payload_backend:
            if instance_backend:
                payload["backend"] = instance_backend

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/file_parse",
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
