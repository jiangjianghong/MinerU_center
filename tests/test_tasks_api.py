from pathlib import Path


def test_pending_list_does_not_recalculate_every_position():
    source = Path("app/api/tasks.py").read_text(encoding="utf-8")
    pending_branch = source.split('if status == "pending":', 1)[1].split(
        'elif status == "running":', 1
    )[0]
    assert "queue.get_position" not in pending_branch
    assert "enumerate" in pending_branch


def test_failed_list_route_precedes_dynamic_task_route():
    source = Path("app/api/tasks.py").read_text(encoding="utf-8")
    assert source.index('@router.get("/failed/list")') < source.index(
        '@router.get("/{task_id}"'
    )
