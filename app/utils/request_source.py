"""Helpers for identifying the client that submitted a task."""

from typing import Protocol


class _RequestLike(Protocol):
    headers: object
    client: object


def get_client_ip(request: _RequestLike) -> str | None:
    """Return the originating client IP from proxy headers or the socket peer."""
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        first_hop = forwarded_for.split(",", 1)[0].strip()
        if first_hop:
            return first_hop

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        real_ip = real_ip.strip()
        if real_ip:
            return real_ip

    client = request.client
    return getattr(client, "host", None) if client else None
