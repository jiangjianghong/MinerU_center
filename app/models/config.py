from pydantic import BaseModel, Field


class CenterConfig(BaseModel):
    # Timeout management
    task_timeout: int = Field(default=300, ge=10, description="Task timeout in seconds")
    queue_timeout: int = Field(default=600, ge=60, description="Queue timeout in seconds")

    # Queue management
    max_queue_size: int = Field(default=100, ge=1, description="Maximum queue length")
    enable_priority: bool = Field(default=True, description="Enable priority scheduling")

    # Retry strategy
    max_retries: int = Field(default=3, ge=0, description="Maximum retry attempts")
    retry_delay: int = Field(default=5, ge=1, description="Retry delay in seconds")

    # Instance management
    health_check_interval: int = Field(default=30, ge=5, description="Health check interval in seconds")
    instance_timeout: int = Field(default=10, ge=1, description="Instance request timeout in seconds")


class ConfigUpdate(BaseModel):
    task_timeout: int | None = None
    queue_timeout: int | None = None
    max_queue_size: int | None = None
    enable_priority: bool | None = None
    max_retries: int | None = None
    retry_delay: int | None = None
    health_check_interval: int | None = None
    instance_timeout: int | None = None
