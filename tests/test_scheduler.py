import pytest
from pathlib import Path

from app.models.config import CenterConfig
from app.models.task import Task, TaskStatus
from app.services.instance_pool import InstancePool
from app.services.queue_manager import QueueManager
from app.services.scheduler import Scheduler


@pytest.mark.asyncio
async def test_cancel_pending_task_persists_cancelled(monkeypatch):
    queue = QueueManager()
    scheduler = Scheduler(queue, InstancePool(), CenterConfig())
    task = Task(payload={"file_name": "a.pdf"})
    queue.enqueue(task)
    updates = []

    async def capture_update(task_id, status, **kwargs):
        updates.append((task_id, status, kwargs))

    monkeypatch.setattr("app.services.scheduler.database.update_task_status", capture_update)
    assert await scheduler.cancel_task(task.id) is True
    assert updates[0][1] == TaskStatus.CANCELLED.value
    assert updates[0][2]["completed_at"].endswith("Z")


def test_scheduler_does_not_replace_request_address_with_instance_url():
    source = Path("app/services/scheduler.py").read_text(encoding="utf-8")
    assert "request_url=f\"{instance.url.rstrip('/')}/file_parse\"" not in source
    assert "request_url=task.request_url" in source
