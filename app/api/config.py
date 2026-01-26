from fastapi import APIRouter, Depends
from typing import Annotated

from ..models.config import CenterConfig, ConfigUpdate
from ..services import database

router = APIRouter(prefix="/api/config", tags=["config"])


def get_config() -> CenterConfig:
    from ..main import config
    return config


def set_config(new_config: CenterConfig) -> None:
    from ..main import set_global_config
    set_global_config(new_config)


@router.get("", response_model=CenterConfig)
async def get_current_config(
    cfg: Annotated[CenterConfig, Depends(get_config)]
):
    """Get current configuration."""
    return cfg


@router.patch("", response_model=CenterConfig)
async def update_config(
    config_update: ConfigUpdate,
    cfg: Annotated[CenterConfig, Depends(get_config)]
):
    """Update configuration (hot update with persistence)."""
    update_data = config_update.model_dump(exclude_unset=True)

    # Create updated config
    new_config = CenterConfig(
        **{**cfg.model_dump(), **update_data}
    )

    # Update in memory
    set_config(new_config)

    # Persist to SQLite
    await database.save_config(new_config)

    return new_config
