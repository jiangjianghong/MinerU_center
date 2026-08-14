from pathlib import Path


def test_stats_module_has_no_websocket_and_returns_dashboard_details():
    source = Path("app/api/stats.py").read_text(encoding="utf-8")
    assert "WebSocket" not in source
    assert '@router.websocket' not in source
    assert '"queued_tasks"' in source
    assert '"running_tasks"' in source
    assert "get_task_stats" in source
    assert '"payload"' not in source


def test_stats_uses_task_request_address_instead_of_instance_url():
    source = Path("app/api/stats.py").read_text(encoding="utf-8")
    assert '"request_url": task.request_url' in source
    assert "instance.url.rstrip" not in source
