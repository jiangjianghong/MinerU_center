#!/usr/bin/env python
"""Run the MinerU Center server."""

import uvicorn
from app.config import settings


def run():
    """Run the server."""
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )


if __name__ == "__main__":
    run()
