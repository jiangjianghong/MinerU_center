import heapq
import threading
from typing import Callable
from ..models.task import Task, TaskStatus


class QueueManager:
    """Thread-safe priority queue manager for tasks."""

    def __init__(self):
        self._queue: list[Task] = []
        self._task_map: dict[str, Task] = {}
        self._lock = threading.Lock()
        self._on_change_callbacks: list[Callable] = []

    def add_change_callback(self, callback: Callable) -> None:
        """Add a callback to be called when queue changes."""
        self._on_change_callbacks.append(callback)

    def _notify_change(self) -> None:
        """Notify all callbacks of queue change."""
        for callback in self._on_change_callbacks:
            try:
                callback()
            except Exception:
                pass

    def enqueue(self, task: Task) -> int:
        """Add task to queue. Returns position in queue."""
        with self._lock:
            if task.id in self._task_map:
                raise ValueError(f"Task {task.id} already in queue")
            heapq.heappush(self._queue, task)
            self._task_map[task.id] = task
            position = self._get_position_unlocked(task.id)
            self._notify_change()
            return position

    def dequeue(self) -> Task | None:
        """Remove and return highest priority task."""
        with self._lock:
            while self._queue:
                task = heapq.heappop(self._queue)
                if task.id in self._task_map:
                    del self._task_map[task.id]
                    self._notify_change()
                    return task
            return None

    def peek(self) -> Task | None:
        """Return highest priority task without removing."""
        with self._lock:
            while self._queue:
                if self._queue[0].id in self._task_map:
                    return self._queue[0]
                heapq.heappop(self._queue)
            return None

    def remove(self, task_id: str) -> bool:
        """Remove task from queue. Returns True if removed."""
        with self._lock:
            if task_id in self._task_map:
                del self._task_map[task_id]
                self._notify_change()
                return True
            return False

    def get(self, task_id: str) -> Task | None:
        """Get task by ID."""
        with self._lock:
            return self._task_map.get(task_id)

    def get_all(self) -> list[Task]:
        """Get all tasks in queue (sorted by priority)."""
        with self._lock:
            tasks = [t for t in self._queue if t.id in self._task_map]
            return sorted(tasks, reverse=True)

    def _get_position_unlocked(self, task_id: str) -> int:
        """Get position of task in queue (1-indexed). Must hold lock."""
        sorted_tasks = sorted(
            [t for t in self._queue if t.id in self._task_map],
            reverse=True
        )
        for i, task in enumerate(sorted_tasks):
            if task.id == task_id:
                return i + 1
        return -1

    def get_position(self, task_id: str) -> int:
        """Get position of task in queue (1-indexed)."""
        with self._lock:
            return self._get_position_unlocked(task_id)

    def size(self) -> int:
        """Return number of tasks in queue."""
        with self._lock:
            return len(self._task_map)

    def clear(self) -> None:
        """Clear all tasks from queue."""
        with self._lock:
            self._queue.clear()
            self._task_map.clear()
            self._notify_change()

    def update_task(self, task_id: str, **kwargs) -> Task | None:
        """Update task properties."""
        with self._lock:
            if task_id not in self._task_map:
                return None
            task = self._task_map[task_id]
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            self._notify_change()
            return task
