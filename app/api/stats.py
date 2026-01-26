from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Annotated
import asyncio
import json

from ..services.queue_manager import QueueManager
from ..services.instance_pool import InstancePool
from ..services.scheduler import Scheduler

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
    sched: Annotated[Scheduler, Depends(get_scheduler)]
):
    """Get current statistics."""
    instances = pool.get_all()
    running_tasks = sched.get_all_running_tasks()
    queued_tasks = queue.get_all()

    total_tasks = sum(inst.total_tasks for inst in instances)
    failed_tasks = sum(inst.failed_tasks for inst in instances)

    idle_instances = sum(1 for inst in instances if inst.status == "idle" and inst.enabled)
    busy_instances = sum(1 for inst in instances if inst.status == "busy")
    offline_instances = sum(1 for inst in instances if inst.status in ["offline", "error"])

    return {
        "queue": {
            "pending": len(queued_tasks),
            "running": len(running_tasks)
        },
        "tasks": {
            "total": total_tasks,
            "completed": total_tasks - failed_tasks,
            "failed": failed_tasks
        },
        "instances": {
            "total": len(instances),
            "idle": idle_instances,
            "busy": busy_instances,
            "offline": offline_instances
        }
    }


# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    queue: Annotated[QueueManager, Depends(get_queue_manager)],
    pool: Annotated[InstancePool, Depends(get_instance_pool)],
    sched: Annotated[Scheduler, Depends(get_scheduler)]
):
    """WebSocket endpoint for real-time stats updates."""
    await manager.connect(websocket)

    try:
        while True:
            # Send stats update every second
            instances = pool.get_all()
            running_tasks = sched.get_all_running_tasks()
            queued_tasks = queue.get_all()

            total_tasks = sum(inst.total_tasks for inst in instances)
            failed_tasks = sum(inst.failed_tasks for inst in instances)

            stats = {
                "type": "stats",
                "data": {
                    "queue": {
                        "pending": len(queued_tasks),
                        "running": len(running_tasks)
                    },
                    "tasks": {
                        "total": total_tasks,
                        "completed": total_tasks - failed_tasks,
                        "failed": failed_tasks
                    },
                    "instances": [
                        {
                            "id": inst.id,
                            "name": inst.name,
                            "status": inst.status,
                            "current_task_id": inst.current_task_id,
                            "enabled": inst.enabled
                        }
                        for inst in instances
                    ],
                    "queued_tasks": [
                        {
                            "id": task.id,
                            "priority": task.priority,
                            "created_at": task.created_at.isoformat(),
                            "status": task.status
                        }
                        for task in queued_tasks[:20]  # Limit to 20
                    ],
                    "running_tasks": [
                        {
                            "id": task.id,
                            "priority": task.priority,
                            "started_at": task.started_at.isoformat() if task.started_at else None,
                            "instance_id": task.instance_id,
                            "status": task.status
                        }
                        for task in running_tasks
                    ]
                }
            }

            await websocket.send_json(stats)
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
