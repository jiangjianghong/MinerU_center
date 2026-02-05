"""SQLite database service for persistent storage."""

import os
import json
import aiosqlite
from typing import Any
from datetime import datetime

from ..models.config import CenterConfig

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "mineru_center.db")


async def init_database() -> None:
    """Initialize the database and create tables."""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        # Config table - stores key-value pairs
        await db.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        # Instances table - stores MinerU instances
        await db.execute("""
            CREATE TABLE IF NOT EXISTS instances (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                enabled INTEGER DEFAULT 1,
                total_tasks INTEGER DEFAULT 0,
                failed_tasks INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)

        # Migrate: add backend column if missing
        try:
            await db.execute("ALTER TABLE instances ADD COLUMN backend TEXT DEFAULT 'pipeline'")
        except Exception:
            pass  # Column already exists

        # Tasks table - stores task history
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'pending',
                priority INTEGER NOT NULL DEFAULT 5,
                payload TEXT,
                file_name TEXT,
                created_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                instance_id TEXT,
                instance_name TEXT,
                error TEXT,
                retry_count INTEGER DEFAULT 0,
                duration REAL
            )
        """)

        # Create indexes for tasks table
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at)
        """)

        await db.commit()


async def load_config() -> CenterConfig:
    """Load configuration from database."""
    config_data = {}

    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT key, value FROM config") as cursor:
                async for row in cursor:
                    key, value = row
                    # Parse JSON value
                    try:
                        config_data[key] = json.loads(value)
                    except json.JSONDecodeError:
                        config_data[key] = value
    except Exception:
        pass

    return CenterConfig(**config_data) if config_data else CenterConfig()


async def save_config(config: CenterConfig) -> None:
    """Save configuration to database."""
    async with aiosqlite.connect(DB_PATH) as db:
        for key, value in config.model_dump().items():
            await db.execute(
                "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                (key, json.dumps(value))
            )
        await db.commit()


async def load_instances() -> list[dict[str, Any]]:
    """Load instances from database."""
    instances = []

    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM instances") as cursor:
                async for row in cursor:
                    instances.append({
                        "id": row["id"],
                        "name": row["name"],
                        "url": row["url"],
                        "enabled": bool(row["enabled"]),
                        "total_tasks": row["total_tasks"],
                        "failed_tasks": row["failed_tasks"],
                        "backend": row["backend"] if "backend" in row.keys() else "pipeline",
                    })
    except Exception:
        pass

    return instances


async def save_instance(instance_id: str, name: str, url: str, enabled: bool = True,
                        total_tasks: int = 0, failed_tasks: int = 0,
                        backend: str = "pipeline") -> None:
    """Save or update an instance in database."""
    from datetime import datetime

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO instances
            (id, name, url, enabled, total_tasks, failed_tasks, created_at, backend)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (instance_id, name, url, int(enabled), total_tasks, failed_tasks,
              datetime.now().isoformat(), backend))
        await db.commit()


async def delete_instance(instance_id: str) -> None:
    """Delete an instance from database."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM instances WHERE id = ?", (instance_id,))
        await db.commit()


async def update_instance_enabled(instance_id: str, enabled: bool) -> None:
    """Update instance enabled status."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE instances SET enabled = ? WHERE id = ?",
            (int(enabled), instance_id)
        )
        await db.commit()


async def update_instance_config(instance_id: str, name: str | None = None,
                                  url: str | None = None, backend: str | None = None) -> None:
    """Update instance configuration (name, url, backend)."""
    updates = []
    params = []
    if name is not None:
        updates.append("name = ?")
        params.append(name)
    if url is not None:
        updates.append("url = ?")
        params.append(url)
    if backend is not None:
        updates.append("backend = ?")
        params.append(backend)

    if not updates:
        return

    params.append(instance_id)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE instances SET {', '.join(updates)} WHERE id = ?",
            tuple(params)
        )
        await db.commit()


async def update_instance_stats(instance_id: str, total_tasks: int, failed_tasks: int) -> None:
    """Update instance task statistics."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE instances SET total_tasks = ?, failed_tasks = ? WHERE id = ?",
            (total_tasks, failed_tasks, instance_id)
        )
        await db.commit()


# ============================================
# Task-related database functions
# ============================================

async def save_task(task_id: str, status: str, priority: int, payload: dict | None,
                    file_name: str | None, created_at: str, started_at: str | None = None,
                    completed_at: str | None = None, instance_id: str | None = None,
                    instance_name: str | None = None, error: str | None = None,
                    retry_count: int = 0, duration: float | None = None) -> None:
    """Save or update a task record in the database.

    Note: payload should NOT include file_base64 to avoid large data storage.
    """
    # Remove file_base64 from payload if present
    if payload:
        payload = {k: v for k, v in payload.items() if k != 'file_base64'}

    payload_json = json.dumps(payload) if payload else None

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO tasks
            (id, status, priority, payload, file_name, created_at, started_at,
             completed_at, instance_id, instance_name, error, retry_count, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (task_id, status, priority, payload_json, file_name, created_at,
              started_at, completed_at, instance_id, instance_name, error,
              retry_count, duration))
        await db.commit()


async def update_task_status(task_id: str, status: str, **kwargs) -> None:
    """Update task status and optional fields.

    Allowed kwargs: started_at, completed_at, instance_id, instance_name,
                   error, retry_count, duration
    """
    updates = ["status = ?"]
    params = [status]

    allowed_fields = ['started_at', 'completed_at', 'instance_id', 'instance_name',
                      'error', 'retry_count', 'duration']

    for field in allowed_fields:
        if field in kwargs:
            updates.append(f"{field} = ?")
            params.append(kwargs[field])

    params.append(task_id)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?",
            tuple(params)
        )
        await db.commit()


async def get_tasks_by_status(status: str | None = None, page: int = 1,
                               page_size: int = 50) -> tuple[list[dict[str, Any]], int]:
    """Get tasks with optional status filter, with pagination.

    Args:
        status: Filter by status (None for all tasks)
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (tasks list, total count)
    """
    tasks = []
    offset = (page - 1) * page_size

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Build query based on status filter
        if status:
            # For "failed" status, also include "timeout" status
            if status == 'failed':
                count_query = "SELECT COUNT(*) FROM tasks WHERE status IN ('failed', 'timeout')"
                data_query = """
                    SELECT * FROM tasks
                    WHERE status IN ('failed', 'timeout')
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """
                count_params = ()
                data_params = (page_size, offset)
            else:
                count_query = "SELECT COUNT(*) FROM tasks WHERE status = ?"
                data_query = """
                    SELECT * FROM tasks
                    WHERE status = ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """
                count_params = (status,)
                data_params = (status, page_size, offset)
        else:
            count_query = "SELECT COUNT(*) FROM tasks"
            data_query = """
                SELECT * FROM tasks
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            count_params = ()
            data_params = (page_size, offset)

        # Get total count
        async with db.execute(count_query, count_params) as cursor:
            row = await cursor.fetchone()
            total = row[0] if row else 0

        # Get paginated data
        async with db.execute(data_query, data_params) as cursor:
            async for row in cursor:
                task_data = {
                    "id": row["id"],
                    "status": row["status"],
                    "priority": row["priority"],
                    "file_name": row["file_name"],
                    "created_at": row["created_at"],
                    "started_at": row["started_at"],
                    "completed_at": row["completed_at"],
                    "instance_id": row["instance_id"],
                    "instance_name": row["instance_name"],
                    "error": row["error"],
                    "retry_count": row["retry_count"],
                    "duration": row["duration"],
                }
                # Parse payload JSON
                if row["payload"]:
                    try:
                        task_data["payload"] = json.loads(row["payload"])
                    except json.JSONDecodeError:
                        task_data["payload"] = None
                else:
                    task_data["payload"] = None
                tasks.append(task_data)

    return tasks, total


async def get_task_stats() -> dict[str, int]:
    """Get task statistics by status.

    Returns:
        Dictionary with counts for each status
    """
    stats = {
        "total": 0,
        "pending": 0,
        "running": 0,
        "completed": 0,
        "failed": 0,  # Includes both "failed" and "timeout"
        "cancelled": 0
    }

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT status, COUNT(*) as count
            FROM tasks
            GROUP BY status
        """) as cursor:
            async for row in cursor:
                status, count = row
                stats["total"] += count
                if status == "pending":
                    stats["pending"] = count
                elif status == "running":
                    stats["running"] = count
                elif status == "completed":
                    stats["completed"] = count
                elif status in ("failed", "timeout"):
                    stats["failed"] += count
                elif status == "cancelled":
                    stats["cancelled"] = count

    return stats


async def get_pending_tasks_position(task_id: str) -> int:
    """Get the position of a pending task in the queue (how many tasks are ahead).

    Returns the number of tasks with:
    - Higher priority, OR
    - Same priority but created earlier
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # First get the task's priority and created_at
        async with db.execute(
            "SELECT priority, created_at FROM tasks WHERE id = ?",
            (task_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                return -1
            priority = row["priority"]
            created_at = row["created_at"]

        # Count tasks ahead in queue
        async with db.execute("""
            SELECT COUNT(*) FROM tasks
            WHERE status = 'pending'
            AND (priority > ? OR (priority = ? AND created_at < ?))
        """, (priority, priority, created_at)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0
