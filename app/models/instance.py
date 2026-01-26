from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class InstanceStatus(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"
    DISABLED = "disabled"


class MinerUInstance(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    url: str
    status: InstanceStatus = InstanceStatus.OFFLINE
    current_task_id: str | None = None
    total_tasks: int = 0
    failed_tasks: int = 0
    last_heartbeat: datetime | None = None
    enabled: bool = True

    class Config:
        use_enum_values = True


class InstanceCreate(BaseModel):
    name: str
    url: str


class InstanceResponse(BaseModel):
    id: str
    name: str
    url: str
    status: str
    current_task_id: str | None
    total_tasks: int
    failed_tasks: int
    last_heartbeat: datetime | None
    enabled: bool
