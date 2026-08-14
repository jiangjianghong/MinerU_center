import pytest

from app.models.task import TaskStatus
from app.services import database
from app.utils.time import to_utc_iso


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    path = tmp_path / "mineru_center.db"
    monkeypatch.setattr(database, "DB_PATH", str(path))
    return path


def test_to_utc_iso_treats_legacy_naive_value_as_utc():
    assert to_utc_iso("2026-08-13T06:59:03") == "2026-08-13T06:59:03Z"


@pytest.mark.asyncio
async def test_init_migrates_request_url_and_fails_interrupted_tasks(temp_db):
    await database.init_database()
    await database.save_task(
        "pending-id", TaskStatus.PENDING.value, 5, {}, "a.pdf", "2026-08-13T06:00:00"
    )
    count = await database.fail_interrupted_tasks("Service restarted before completion")
    rows, _ = await database.get_tasks_by_status("failed", 1, 50)
    assert count == 1
    assert rows[0]["request_url"] is None
    assert rows[0]["completed_at"].endswith("Z")


@pytest.mark.asyncio
async def test_clear_legacy_instance_request_urls(temp_db):
    await database.init_database()
    await database.save_task(
        "legacy-id", TaskStatus.COMPLETED.value, 5, {}, "a.pdf",
        "2026-08-13T06:00:00", request_url="http://mineru:8000/file_parse"
    )
    await database.save_task(
        "client-id", TaskStatus.COMPLETED.value, 5, {}, "b.pdf",
        "2026-08-13T06:00:00", request_url="203.0.113.20"
    )
    count = await database.clear_legacy_request_urls()
    rows, _ = await database.get_tasks_by_status("completed", 1, 50)
    by_id = {row["id"]: row for row in rows}
    assert count == 1
    assert by_id["legacy-id"]["request_url"] is None
    assert by_id["client-id"]["request_url"] == "203.0.113.20"
