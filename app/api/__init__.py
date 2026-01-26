from .tasks import router as tasks_router
from .instances import router as instances_router
from .config import router as config_router
from .stats import router as stats_router

__all__ = ["tasks_router", "instances_router", "config_router", "stats_router"]
