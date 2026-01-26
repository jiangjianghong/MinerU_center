import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .models.config import CenterConfig
from .models.instance import InstanceStatus
from .services.queue_manager import QueueManager
from .services.instance_pool import InstancePool
from .services.scheduler import Scheduler
from .services import database
from .api import tasks_router, instances_router, config_router, stats_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global instances
config = CenterConfig()
queue_manager = QueueManager()
instance_pool = InstancePool()
scheduler = Scheduler(queue_manager, instance_pool, config)

# Health check task
health_check_task: asyncio.Task | None = None


def set_global_config(new_config: CenterConfig) -> None:
    """Update global config."""
    global config
    config = new_config
    scheduler.config = new_config


async def save_config_to_db(new_config: CenterConfig) -> None:
    """Save config to database."""
    await database.save_config(new_config)


async def health_check_loop():
    """Periodic health check loop."""
    while True:
        try:
            await instance_pool.health_check(config.instance_timeout)
            await asyncio.sleep(config.health_check_interval)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Health check error: {e}")
            await asyncio.sleep(5)


async def load_persisted_data():
    """Load persisted configuration and instances from database."""
    global config

    # Initialize database
    await database.init_database()

    # Load config
    config = await database.load_config()
    scheduler.config = config
    logger.info(f"Loaded config from database: task_timeout={config.task_timeout}s")

    # Load instances
    instances = await database.load_instances()
    for inst_data in instances:
        instance = instance_pool.add_instance(inst_data["url"], inst_data["name"])
        # Override the auto-generated ID with the persisted one
        instance_pool._instances.pop(instance.id)
        instance.id = inst_data["id"]
        instance.enabled = inst_data["enabled"]
        instance.total_tasks = inst_data["total_tasks"]
        instance.failed_tasks = inst_data["failed_tasks"]
        instance.status = InstanceStatus.IDLE if instance.enabled else InstanceStatus.DISABLED
        instance_pool._instances[instance.id] = instance

    logger.info(f"Loaded {len(instances)} instances from database")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global health_check_task

    # Startup
    logger.info("Starting MinerU Center...")

    # Load persisted data from SQLite
    await load_persisted_data()

    await scheduler.start()
    health_check_task = asyncio.create_task(health_check_loop())
    logger.info("MinerU Center started successfully")

    yield

    # Shutdown
    logger.info("Shutting down MinerU Center...")
    await scheduler.stop()
    if health_check_task:
        health_check_task.cancel()
        try:
            await health_check_task
        except asyncio.CancelledError:
            pass
    logger.info("MinerU Center shut down successfully")


# Create FastAPI app
app = FastAPI(
    title="MinerU Center",
    description="Unified management center for multiple MinerU instances",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(tasks_router)
app.include_router(instances_router)
app.include_router(config_router)
app.include_router(stats_router)


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


# Serve static files for frontend
static_dir = settings.static_dir


@app.get("/ui")
async def serve_frontend_root():
    """Serve frontend application."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend not built", "message": "Run 'npm run build' in the ui directory"}


# Mount static files - must be after explicit routes but will handle /ui/* paths
if os.path.exists(static_dir):
    app.mount("/ui", StaticFiles(directory=static_dir, html=True), name="ui")


@app.get("/")
async def root():
    """Root endpoint - redirect to UI."""
    return {"message": "Welcome to MinerU Center", "ui": "/ui", "api": "/docs"}
