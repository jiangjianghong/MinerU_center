from fastapi import APIRouter, Depends
from typing import Annotated

from ..services import database
from ..services.queue_manager import QueueManager
from ..services.instance_pool import InstancePool
from ..services.scheduler import Scheduler
from ..utils.time import to_utc_iso

router = APIRouter(prefix="/api/stats", tags=["stats"])


def get_queue_manager() -> QueueManager:
    from ..main import queue_manager
    return queue_manager


def get_instance_pool() -> InstancePool:
    from ..main import instance_pool
    return instance_pool


def get_scheduler() -> Scheduler:
    from ..main import scheduler
    return scheduler


@router.get("")
async def get_stats(
    queue: Annotated[QueueManager, Depends(get_queue_manager)],
    pool: Annotated[InstancePool, Depends(get_instance_pool)],
    sched: Annotated[Scheduler, Depends(get_scheduler)],
):
    """Return one consistent, lightweight dashboard snapshot."""
    instances = pool.get_all()
    queued_tasks = queue.get_all()
    running_tasks = sched.get_all_running_tasks()
    task_stats = await database.get_task_stats()

    return {
        "queue": {
            "pending": len(queued_tasks),
            "running": len(running_tasks),
        },
        "tasks": task_stats,
        "instances": [
            {
                "id": inst.id,
                "name": inst.name,
                "url": inst.url,
                "status": inst.status,
                "current_task_id": inst.current_task_id,
                "enabled": inst.enabled,
                "backend": str(inst.backend),
            }
            for inst in instances
        ],
        "queued_tasks": [
            {
                "id": task.id,
                "priority": task.priority,
                "file_name": task.payload.get("file_name") if task.payload else None,
                "created_at": to_utc_iso(task.created_at),
                "status": task.status,
                "position": position,
                "request_url": None,
            }
            for position, task in enumerate(queued_tasks, start=1)
        ],
        "running_tasks": [
            {
                "id": task.id,
                "priority": task.priority,
                "file_name": task.payload.get("file_name") if task.payload else None,
                "created_at": to_utc_iso(task.created_at),
                "started_at": to_utc_iso(task.started_at),
                "instance_id": task.instance_id,
                "status": task.status,
                "request_url": (
                    f"{instance.url.rstrip('/')}/file_parse" if instance else None
                ),
            }
            for task in running_tasks
            for instance in [pool.get_instance(task.instance_id) if task.instance_id else None]
        ],
    }
