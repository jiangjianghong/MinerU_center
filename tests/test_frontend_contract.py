from pathlib import Path


def frontend_source() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in Path("ui/src").rglob("*")
        if path.is_file()
    )


def test_frontend_has_no_websocket_code():
    source = frontend_source()
    assert "new WebSocket" not in source
    assert "connectWebSocket" not in source
    assert "stats/ws" not in source


def test_store_uses_adaptive_non_overlapping_polling():
    source = Path("ui/src/stores/index.js").read_text(encoding="utf-8")
    for interval in ("2000", "5000", "15000", "30000"):
        assert interval in source
    assert "pollInFlight" in source
    assert "visibilitychange" in source


def test_task_list_displays_request_url():
    source = Path("ui/src/components/TaskListDialog.vue").read_text(encoding="utf-8")
    assert "task.request_url" in source
    assert "taskList.requestUrl" in source


def test_failed_tasks_are_loaded_over_rest():
    source = Path("ui/src/stores/index.js").read_text(encoding="utf-8")
    assert "function fetchFailedTasks" in source
    assert "tasksApi.listFailed()" in source
    assert "fetchFailedTasks," in source
