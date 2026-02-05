from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated

from ..models.instance import MinerUInstance, InstanceCreate, InstanceUpdate, InstanceResponse, InstanceStatus
from ..services.instance_pool import InstancePool
from ..services import database

router = APIRouter(prefix="/api/instances", tags=["instances"])


def get_instance_pool() -> InstancePool:
    from ..main import instance_pool
    return instance_pool


@router.get("", response_model=list[InstanceResponse])
async def list_instances(
    pool: Annotated[InstancePool, Depends(get_instance_pool)]
):
    """Get all instances."""
    instances = pool.get_all()
    return [
        InstanceResponse(
            id=inst.id,
            name=inst.name,
            url=inst.url,
            status=inst.status,
            current_task_id=inst.current_task_id,
            total_tasks=inst.total_tasks,
            failed_tasks=inst.failed_tasks,
            last_heartbeat=inst.last_heartbeat,
            enabled=inst.enabled,
            backend=str(inst.backend)
        )
        for inst in instances
    ]


@router.post("", response_model=InstanceResponse)
async def add_instance(
    instance_create: InstanceCreate,
    pool: Annotated[InstancePool, Depends(get_instance_pool)]
):
    """Add a new instance."""
    instance = pool.add_instance(
        url=instance_create.url,
        name=instance_create.name,
        backend=instance_create.backend.value
    )

    # Persist to SQLite
    await database.save_instance(
        instance_id=instance.id,
        name=instance.name,
        url=instance.url,
        enabled=instance.enabled,
        total_tasks=instance.total_tasks,
        failed_tasks=instance.failed_tasks,
        backend=str(instance.backend)
    )

    return InstanceResponse(
        id=instance.id,
        name=instance.name,
        url=instance.url,
        status=instance.status,
        current_task_id=instance.current_task_id,
        total_tasks=instance.total_tasks,
        failed_tasks=instance.failed_tasks,
        last_heartbeat=instance.last_heartbeat,
        enabled=instance.enabled,
        backend=str(instance.backend)
    )


@router.delete("/{instance_id}")
async def remove_instance(
    instance_id: str,
    pool: Annotated[InstancePool, Depends(get_instance_pool)]
):
    """Remove an instance."""
    instance = pool.get_instance(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")

    if instance.current_task_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot remove instance with running task"
        )

    if pool.remove_instance(instance_id):
        # Delete from SQLite
        await database.delete_instance(instance_id)
        return {"message": "Instance removed", "instance_id": instance_id}
    raise HTTPException(status_code=404, detail="Instance not found")


@router.patch("/{instance_id}", response_model=InstanceResponse)
async def update_instance(
    instance_id: str,
    instance_update: InstanceUpdate,
    pool: Annotated[InstancePool, Depends(get_instance_pool)]
):
    """Update an instance configuration."""
    instance = pool.get_instance(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")

    # Cannot update URL while instance has a running task
    if instance_update.url and instance.current_task_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot update URL while instance has running task"
        )

    # Update in pool
    updated = pool.update_instance(
        instance_id,
        name=instance_update.name,
        url=instance_update.url,
        backend=instance_update.backend.value if instance_update.backend else None
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Instance not found")

    # Persist to SQLite
    await database.update_instance_config(
        instance_id,
        name=instance_update.name,
        url=instance_update.url,
        backend=instance_update.backend.value if instance_update.backend else None
    )

    return InstanceResponse(
        id=updated.id,
        name=updated.name,
        url=updated.url,
        status=updated.status,
        current_task_id=updated.current_task_id,
        total_tasks=updated.total_tasks,
        failed_tasks=updated.failed_tasks,
        last_heartbeat=updated.last_heartbeat,
        enabled=updated.enabled,
        backend=str(updated.backend)
    )


@router.post("/{instance_id}/enable")
async def enable_instance(
    instance_id: str,
    pool: Annotated[InstancePool, Depends(get_instance_pool)]
):
    """Enable an instance."""
    if pool.enable_instance(instance_id):
        pool.set_status(instance_id, InstanceStatus.IDLE)
        # Persist to SQLite
        await database.update_instance_enabled(instance_id, True)
        return {"message": "Instance enabled", "instance_id": instance_id}
    raise HTTPException(status_code=404, detail="Instance not found")


@router.post("/{instance_id}/disable")
async def disable_instance(
    instance_id: str,
    pool: Annotated[InstancePool, Depends(get_instance_pool)]
):
    """Disable an instance."""
    if pool.disable_instance(instance_id):
        # Persist to SQLite
        await database.update_instance_enabled(instance_id, False)
        return {"message": "Instance disabled", "instance_id": instance_id}
    raise HTTPException(status_code=404, detail="Instance not found")
