from types import SimpleNamespace

from app.utils.request_source import get_client_ip


def test_client_ip_prefers_first_forwarded_address():
    request = SimpleNamespace(
        headers={
            "x-forwarded-for": "203.0.113.20, 10.0.0.8",
            "x-real-ip": "198.51.100.4",
        },
        client=SimpleNamespace(host="127.0.0.1"),
    )
    assert get_client_ip(request) == "203.0.113.20"


def test_client_ip_falls_back_to_real_ip_then_socket_peer():
    request = SimpleNamespace(
        headers={"x-real-ip": "198.51.100.4"},
        client=SimpleNamespace(host="127.0.0.1"),
    )
    assert get_client_ip(request) == "198.51.100.4"

    request.headers = {}
    assert get_client_ip(request) == "127.0.0.1"


def test_client_ip_returns_none_without_connection_metadata():
    request = SimpleNamespace(headers={}, client=None)
    assert get_client_ip(request) is None
