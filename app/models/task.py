from enum import Enum
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field
import uuid


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    payload: dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    priority: int = Field(default=5, ge=1, le=10)
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: dict[str, Any] | None = None
    error: str | None = None
    retry_count: int = 0
    instance_id: str | None = None

    def __lt__(self, other: "Task") -> bool:
        # Higher priority comes first (max heap behavior)
        if self.priority != other.priority:
            return self.priority > other.priority
        # Earlier created_at comes first for same priority
        return self.created_at < other.created_at

    class Config:
        use_enum_values = True


class TaskCreate(BaseModel):
    async_mode: bool = Field(default=False, alias="async")
    priority: int = Field(default=5, ge=1, le=10)
    payload: dict[str, Any] = Field(default_factory=dict)

    class Config:
        populate_by_name = True


class TaskResponse(BaseModel):
    task_id: str
    status: str
    position: int | None = None
    result: dict[str, Any] | None = None
    error: str | None = None
