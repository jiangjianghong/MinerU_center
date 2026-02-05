import base64
from typing import Any
import httpx


class MinerUClient:
    """HTTP client for MinerU instances."""

    def __init__(self, base_url: str, timeout: int = 300):
        self.base_url = base_url.rstrip("/")
        # Add extra buffer to httpx timeout so asyncio.wait_for fires first
        self.timeout = timeout + 10

    async def submit_task(self, payload: dict[str, Any], instance_backend: str | None = None) -> dict[str, Any]:
        """Submit a task to MinerU instance via multipart/form-data.

        Args:
            payload: The task payload containing file_base64, file_name, and form fields.
            instance_backend: The backend configured on the target instance.
                If payload backend is 'auto' or missing, it will be replaced
                with the instance's backend value.
        """
        # Backend conversion logic
        payload_backend = payload.get("backend")
        if payload_backend == "auto" or not payload_backend:
            if instance_backend:
                payload["backend"] = instance_backend

        # Decode file from base64
        file_base64 = payload.get("file_base64", "")
        file_name = payload.get("file_name", "document.pdf")
        file_content = base64.b64decode(file_base64)

        # Build form data (exclude file-related keys)
        exclude_keys = {"file_base64", "file_name"}
        data = {k: v for k, v in payload.items() if k not in exclude_keys}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/file_parse",
                files={"files": (file_name, file_content, "application/pdf")},
                data=data,
            )
            response.raise_for_status()
            return response.json()

    async def health_check(self, timeout: int = 10) -> bool:
        """Check if instance is healthy."""
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(f"{self.base_url}/openapi.json")
                return response.status_code == 200
        except Exception:
            return False
