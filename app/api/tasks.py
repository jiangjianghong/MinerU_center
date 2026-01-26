from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated

from ..models.task import Task, TaskCreate, TaskResponse, TaskStatus
from ..services.queue_manager import QueueManager
from ..services.scheduler import Scheduler
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
    status: str | None = None
):
    """Get list of all tasks."""
    tasks = []

    # Get queued tasks
    for task in queue.get_all():
        if status is None or task.status == status:
            tasks.append({
                "task_id": task.id,
                "status": task.status,
                "priority": task.priority,
                "created_at": task.created_at.isoformat(),
                "position": queue.get_position(task.id)
            })

    # Get running tasks
    for task in sched.get_all_running_tasks():
        if status is None or task.status == status:
            tasks.append({
                "task_id": task.id,
                "status": task.status,
                "priority": task.priority,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "instance_id": task.instance_id
            })

    return {"tasks": tasks, "total": len(tasks)}


@router.delete("/{task_id}")
async def cancel_task(
    task_id: str,
    sched: Annotated[Scheduler, Depends(get_scheduler)]
):
    """Cancel a task."""
    if await sched.cancel_task(task_id):
        return {"message": "Task cancelled", "task_id": task_id}
    raise HTTPException(status_code=404, detail="Task not found or already completed")
