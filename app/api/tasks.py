from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated

from ..models.task import Task, TaskCreate, TaskResponse, TaskStatus
from ..services.queue_manager import QueueManager
from ..services.scheduler import Scheduler
from ..services import database
from ..models.config import CenterConfig

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def get_queue_manager() -> QueueManager:
    from ..main import queue_manager
    return queue_manager


def get_scheduler() -> Scheduler:
    from ..main import scheduler
    return scheduler


def get_config() -> CenterConfig:
    from ..main import config
    return config


@router.post("", response_model=TaskResponse)
async def create_task(
    task_create: TaskCreate,
    queue: Annotated[QueueManager, Depends(get_queue_manager)],
    sched: Annotated[Scheduler, Depends(get_scheduler)],
    cfg: Annotated[CenterConfig, Depends(get_config)]
):
    """Submit a new task."""
    # Check queue size
    if queue.size() >= cfg.max_queue_size:
        raise HTTPException(status_code=429, detail="Queue is full")

    # Create task
    task = Task(
        payload=task_create.payload,
        priority=task_create.priority if cfg.enable_priority else 5
    )

    # Save task to database
    file_name = task_create.payload.get("file_name") if task_create.payload else None
    try:
        await database.save_task(
            task_id=task.id,
            status=task.status.value,
            priority=task.priority,
            payload=task_create.payload,
            file_name=file_name,
            created_at=task.created_at.isoformat()
        )
    except Exception as e:
        import logging
        logging.error(f"Failed to save task to database: {e}")

    # Add to queue
    position = queue.enqueue(task)

    if task_create.async_mode:
        # Async mode: return immediately
        return TaskResponse(
            task_id=task.id,
            status=task.status,
            position=position
        )
    else:
        # Sync mode: wait for completion
        completed_task = await sched.wait_for_task(task.id)
        if completed_task:
            return TaskResponse(
                task_id=completed_task.id,
                status=completed_task.status,
                result=completed_task.result,
                error=completed_task.error
            )
        else:
            raise HTTPException(status_code=500, detail="Task execution failed")


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    queue: Annotated[QueueManager, Depends(get_queue_manager)],
    sched: Annotated[Scheduler, Depends(get_scheduler)]
):
    """Get task status and result."""
    # Check queue
    task = queue.get(task_id)
    if task:
        return TaskResponse(
            task_id=task.id,
            status=task.status,
            position=queue.get_position(task_id),
            error=task.error
        )

    # Check running tasks
    task = sched.get_running_task(task_id)
    if task:
        return TaskResponse(
            task_id=task.id,
            status=task.status,
            result=task.result,
            error=task.error
        )

    raise HTTPException(status_code=404, detail="Task not found")


@router.get("")
async def list_tasks(
    queue: Annotated[QueueManager, Depends(get_queue_manager)],
    sched: Annotated[Scheduler, Depends(get_scheduler)],
    status: str | None = None,
    page: int = 1,
    page_size: int = 50
):
    """Get list of tasks with pagination.

    Args:
        status: Filter by status (pending, running, completed, failed, or None for all)
        page: Page number (1-indexed)
        page_size: Number of items per page (default 50)
    """
    # For pending and running status, combine database data with in-memory data for accuracy
    if status == "pending":
        # Get pending tasks from queue (in-memory) for accurate queue position
        tasks = []
        for task in queue.get_all():
            tasks.append({
                "task_id": task.id,
                "status": task.status,
                "priority": task.priority,
                "file_name": task.payload.get("file_name") if task.payload else None,
                "created_at": task.created_at.isoformat(),
                "position": queue.get_position(task.id)
            })

        total = len(tasks)
        # Apply pagination
        start = (page - 1) * page_size
        end = start + page_size
        tasks = tasks[start:end]

        return {"tasks": tasks, "total": total, "page": page, "page_size": page_size}

    elif status == "running":
        # Get running tasks from scheduler (in-memory) for accuracy
        tasks = []
        for task in sched.get_all_running_tasks():
            instance = None
            if task.instance_id:
                from ..main import instance_pool
                instance = instance_pool.get_instance(task.instance_id)

            tasks.append({
                "task_id": task.id,
                "status": task.status,
                "priority": task.priority,
                "file_name": task.payload.get("file_name") if task.payload else None,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "instance_id": task.instance_id,
                "instance_name": instance.name if instance else None,
                "retry_count": task.retry_count
            })

        total = len(tasks)
        # Apply pagination
        start = (page - 1) * page_size
        end = start + page_size
        tasks = tasks[start:end]

        return {"tasks": tasks, "total": total, "page": page, "page_size": page_size}

    else:
        # For completed, failed, or all tasks - query from database
        db_tasks, total = await database.get_tasks_by_status(status, page, page_size)

        tasks = []
        for task in db_tasks:
            tasks.append({
                "task_id": task["id"],
                "status": task["status"],
                "priority": task["priority"],
                "file_name": task["file_name"],
                "created_at": task["created_at"],
                "started_at": task["started_at"],
                "completed_at": task["completed_at"],
                "instance_id": task["instance_id"],
                "instance_name": task["instance_name"],
                "error": task["error"],
                "retry_count": task["retry_count"],
                "duration": task["duration"]
            })

        return {"tasks": tasks, "total": total, "page": page, "page_size": page_size}


@router.delete("/{task_id}")
async def cancel_task(
    task_id: str,
    sched: Annotated[Scheduler, Depends(get_scheduler)]
):
    """Cancel a task."""
    if await sched.cancel_task(task_id):
        return {"message": "Task cancelled", "task_id": task_id}
    raise HTTPException(status_code=404, detail="Task not found or already completed")


@router.get("/failed/list")
async def list_failed_tasks(
    sched: Annotated[Scheduler, Depends(get_scheduler)]
):
    """Get list of all failed tasks."""
    tasks = []
    for task in sched.get_all_failed_tasks():
        tasks.append({
            "task_id": task.id,
            "status": task.status,
            "priority": task.priority,
            "payload": task.payload,
            "error": task.error,
            "retry_count": task.retry_count,
            "created_at": task.created_at.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        })
    return {"tasks": tasks, "total": len(tasks)}


@router.post("/{task_id}/retry")
async def retry_task(
    task_id: str,
    sched: Annotated[Scheduler, Depends(get_scheduler)]
):
    """Retry a single failed task."""
    if await sched.retry_failed_task(task_id):
        return {"message": "Task requeued for retry", "task_id": task_id}
    raise HTTPException(status_code=404, detail="Failed task not found")


@router.post("/retry-all")
async def retry_all_tasks(
    sched: Annotated[Scheduler, Depends(get_scheduler)]
):
    """Retry all failed tasks."""
    count = await sched.retry_all_failed_tasks()
    return {"message": f"Requeued {count} tasks for retry", "count": count}
