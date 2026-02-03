"""SQLite database service for persistent storage."""

import os
import json
import aiosqlite
from typing import Any

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
