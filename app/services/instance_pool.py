import threading
from datetime import datetime
from typing import Callable
import httpx

from ..models.instance import MinerUInstance, InstanceStatus, BackendType


class InstancePool:
    """MinerU instance pool manager."""

    def __init__(self, health_check_timeout: int = 10):
        self._instances: dict[str, MinerUInstance] = {}
        self._lock = threading.Lock()
        self._health_check_timeout = health_check_timeout
        self._on_change_callbacks: list[Callable] = []

    def add_change_callback(self, callback: Callable) -> None:
        """Add a callback to be called when pool changes."""
        self._on_change_callbacks.append(callback)

    def _notify_change(self) -> None:
        """Notify all callbacks of pool change."""
        for callback in self._on_change_callbacks:
            try:
                callback()
            except Exception:
                pass

    def add_instance(self, url: str, name: str, backend: str = "pipeline") -> MinerUInstance:
        """Add a new instance to the pool."""
        backend_type = BackendType(backend) if backend else BackendType.PIPELINE
        instance = MinerUInstance(name=name, url=url.rstrip("/"), backend=backend_type)
        with self._lock:
            self._instances[instance.id] = instance
            self._notify_change()
        return instance

    def remove_instance(self, instance_id: str) -> bool:
        """Remove instance from pool."""
        with self._lock:
            if instance_id in self._instances:
                del self._instances[instance_id]
                self._notify_change()
                return True
            return False

    def get_instance(self, instance_id: str) -> MinerUInstance | None:
        """Get instance by ID."""
        with self._lock:
            return self._instances.get(instance_id)

    def get_idle_instance(self) -> MinerUInstance | None:
        """Get first available idle instance."""
        with self._lock:
            for instance in self._instances.values():
                if instance.status == InstanceStatus.IDLE and instance.enabled:
                    return instance
            return None

    def set_status(self, instance_id: str, status: InstanceStatus) -> None:
        """Set instance status."""
        with self._lock:
            if instance_id in self._instances:
                self._instances[instance_id].status = status
                self._notify_change()

    def set_current_task(self, instance_id: str, task_id: str | None) -> None:
        """Set current task for instance."""
        with self._lock:
            if instance_id in self._instances:
                self._instances[instance_id].current_task_id = task_id
                self._notify_change()

    def increment_total_tasks(self, instance_id: str) -> None:
        """Increment total tasks counter."""
        with self._lock:
            if instance_id in self._instances:
                self._instances[instance_id].total_tasks += 1

    def increment_failed_tasks(self, instance_id: str) -> None:
        """Increment failed tasks counter."""
        with self._lock:
            if instance_id in self._instances:
                self._instances[instance_id].failed_tasks += 1

    def update_heartbeat(self, instance_id: str) -> None:
        """Update last heartbeat time."""
        with self._lock:
            if instance_id in self._instances:
                self._instances[instance_id].last_heartbeat = datetime.now()

    def enable_instance(self, instance_id: str) -> bool:
        """Enable instance."""
        with self._lock:
            if instance_id in self._instances:
                self._instances[instance_id].enabled = True
                self._notify_change()
                return True
            return False

    def disable_instance(self, instance_id: str) -> bool:
        """Disable instance."""
        with self._lock:
            if instance_id in self._instances:
                instance = self._instances[instance_id]
                instance.enabled = False
                instance.status = InstanceStatus.DISABLED
                self._notify_change()
                return True
            return False

    def get_all(self) -> list[MinerUInstance]:
        """Get all instances."""
        with self._lock:
            return list(self._instances.values())

    async def health_check(self, timeout: int | None = None) -> None:
        """Check health of all instances."""
        timeout = timeout or self._health_check_timeout
        instances = self.get_all()

        for instance in instances:
            if not instance.enabled:
                continue

            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(f"{instance.url}/health")
                    if response.status_code == 200:
                        self.update_heartbeat(instance.id)
                        if instance.status == InstanceStatus.OFFLINE:
                            self.set_status(instance.id, InstanceStatus.IDLE)
                    else:
                        if instance.current_task_id is None:
                            self.set_status(instance.id, InstanceStatus.ERROR)
            except Exception:
                if instance.current_task_id is None:
                    self.set_status(instance.id, InstanceStatus.OFFLINE)
