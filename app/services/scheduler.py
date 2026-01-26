import asyncio
import logging
from datetime import datetime
from typing import TYPE_CHECKING

from ..models.task import Task, TaskStatus
from ..models.instance import InstanceStatus
from .mineru_client import MinerUClient

if TYPE_CHECKING:
    from .queue_manager import QueueManager
    from .instance_pool import InstancePool
    from ..models.config import CenterConfig

logger = logging.getLogger(__name__)


class Scheduler:
    """Core task scheduler - runs asynchronously."""

    def __init__(
        self,
        queue_manager: "QueueManager",
        instance_pool: "InstancePool",
        config: "CenterConfig"
    ):
        self.queue = queue_manager
        self.pool = instance_pool
        self.config = config
        self._running = False
        self._task: asyncio.Task | None = None
        self._running_tasks: dict[str, Task] = {}
        self._task_futures: dict[str, asyncio.Future] = {}
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        """Start the scheduler loop."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Scheduler started")

    async def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Scheduler stopped")

    async def _run_loop(self) -> None:
        """Main scheduler loop."""
        while self._running:
            try:
                await self._dispatch_pending_tasks()
                await self._check_timeouts()
                await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(1)

    async def _dispatch_pending_tasks(self) -> None:
        """Dispatch pending tasks to available instances."""
        while True:
            instance = self.pool.get_idle_instance()
            if not instance:
                break

            task = self.queue.dequeue()
            if not task:
                break

            await self._dispatch_task(task, instance.id)

    async def _dispatch_task(self, task: Task, instance_id: str) -> None:
        """Dispatch a single task to an instance."""
        instance = self.pool.get_instance(instance_id)
        if not instance:
            # Re-queue the task
            self.queue.enqueue(task)
            return

        # Update states
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        task.instance_id = instance_id

        self.pool.set_status(instance_id, InstanceStatus.BUSY)
        self.pool.set_current_task(instance_id, task.id)
        self.pool.increment_total_tasks(instance_id)

        async with self._lock:
            self._running_tasks[task.id] = task

        # Create async task for execution
        asyncio.create_task(self._execute_task(task, instance_id))

    async def _execute_task(self, task: Task, instance_id: str) -> None:
        """Execute task on instance."""
        instance = self.pool.get_instance(instance_id)
        if not instance:
            await self._handle_task_failure(task, "Instance not found")
            return

        client = MinerUClient(instance.url, self.config.task_timeout)

        try:
            result = await asyncio.wait_for(
                client.submit_task(task.payload),
                timeout=self.config.task_timeout
            )
            await self._handle_task_success(task, result)
        except asyncio.TimeoutError:
            await self._handle_task_timeout(task)
        except Exception as e:
            await self._handle_task_failure(task, str(e))
        finally:
            self._release_instance(instance_id)

    async def _handle_task_success(self, task: Task, result: dict) -> None:
        """Handle successful task completion."""
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        task.result = result

        async with self._lock:
            self._running_tasks.pop(task.id, None)
            if task.id in self._task_futures:
                self._task_futures[task.id].set_result(task)

        logger.info(f"Task {task.id} completed successfully")

    async def _handle_task_failure(self, task: Task, error: str) -> None:
        """Handle task failure."""
        task.error = error

        if task.instance_id:
            self.pool.increment_failed_tasks(task.instance_id)

        if task.retry_count < self.config.max_retries:
            task.retry_count += 1
            task.status = TaskStatus.PENDING
            task.started_at = None
            task.instance_id = None
            await asyncio.sleep(self.config.retry_delay)
            self.queue.enqueue(task)
            logger.info(f"Task {task.id} requeued (retry {task.retry_count})")
        else:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            async with self._lock:
                self._running_tasks.pop(task.id, None)
                if task.id in self._task_futures:
                    self._task_futures[task.id].set_result(task)
            logger.error(f"Task {task.id} failed: {error}")

    async def _handle_task_timeout(self, task: Task) -> None:
        """Handle task timeout."""
        task.error = "Task execution timeout"

        if task.instance_id:
            self.pool.increment_failed_tasks(task.instance_id)

        if task.retry_count < self.config.max_retries:
            task.retry_count += 1
            task.status = TaskStatus.PENDING
            task.started_at = None
            task.instance_id = None
            await asyncio.sleep(self.config.retry_delay)
            self.queue.enqueue(task)
            logger.info(f"Task {task.id} requeued after timeout (retry {task.retry_count})")
        else:
            task.status = TaskStatus.TIMEOUT
            task.completed_at = datetime.now()
            async with self._lock:
                self._running_tasks.pop(task.id, None)
                if task.id in self._task_futures:
                    self._task_futures[task.id].set_result(task)
            logger.error(f"Task {task.id} timed out")

    def _release_instance(self, instance_id: str) -> None:
        """Release instance after task completion."""
        instance = self.pool.get_instance(instance_id)
        if instance and instance.enabled:
            self.pool.set_status(instance_id, InstanceStatus.IDLE)
        self.pool.set_current_task(instance_id, None)

    async def _check_timeouts(self) -> None:
        """Check for queue timeouts."""
        now = datetime.now()
        queue_tasks = self.queue.get_all()

        for task in queue_tasks:
            elapsed = (now - task.created_at).total_seconds()
            if elapsed > self.config.queue_timeout:
                self.queue.remove(task.id)
                task.status = TaskStatus.TIMEOUT
                task.error = "Queue timeout"
                task.completed_at = now
                async with self._lock:
                    if task.id in self._task_futures:
                        self._task_futures[task.id].set_result(task)
                logger.warning(f"Task {task.id} timed out in queue")

    async def wait_for_task(self, task_id: str) -> Task | None:
        """Wait for task to complete and return result."""
        async with self._lock:
            if task_id in self._running_tasks:
                task = self._running_tasks[task_id]
            else:
                task = self.queue.get(task_id)

            if not task:
                return None

            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.TIMEOUT, TaskStatus.CANCELLED]:
                return task

            if task_id not in self._task_futures:
                self._task_futures[task_id] = asyncio.get_event_loop().create_future()

        try:
            result = await self._task_futures[task_id]
            return result
        finally:
            async with self._lock:
                self._task_futures.pop(task_id, None)

    def get_running_task(self, task_id: str) -> Task | None:
        """Get a running task by ID."""
        return self._running_tasks.get(task_id)

    def get_all_running_tasks(self) -> list[Task]:
        """Get all running tasks."""
        return list(self._running_tasks.values())

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task."""
        # Try to remove from queue
        if self.queue.remove(task_id):
            return True

        # Check if running
        async with self._lock:
            if task_id in self._running_tasks:
                task = self._running_tasks[task_id]
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.now()
                self._running_tasks.pop(task_id, None)
                if task_id in self._task_futures:
                    self._task_futures[task_id].set_result(task)
                return True

        return False
