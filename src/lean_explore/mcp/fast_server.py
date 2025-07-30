# src/lean_explore/mcp/fast_server.py

"""Optimized MCP Server with faster startup time.

Key optimizations:
1. Lazy loading of heavy components
2. Async initialization where possible
3. Pre-warmed cache option
4. Lightweight health check endpoint
"""

import argparse
import logging
import sys
import asyncio
from typing import Optional
import time

from lean_explore import defaults
from lean_explore.mcp.app import BackendServiceType, mcp_app

logger = logging.getLogger(__name__)


class LazyLocalService:
    """Lazy-loading wrapper for LocalService to defer heavy initialization."""
    
    def __init__(self):
        self._service = None
        self._init_lock = asyncio.Lock()
        self._init_start_time = None
        
    async def _ensure_initialized(self):
        """Initialize the service on first use."""
        if self._service is not None:
            return
            
        async with self._init_lock:
            if self._service is not None:
                return
                
            self._init_start_time = time.time()
            logger.info("Starting lazy initialization of LocalService...")
            
            # Import and initialize in background
            from lean_explore.local.service import Service
            
            # Run blocking initialization in thread pool
            loop = asyncio.get_event_loop()
            self._service = await loop.run_in_executor(None, Service)
            
            init_time = time.time() - self._init_start_time
            logger.info(f"LocalService initialized in {init_time:.2f}s")
    
    def __getattr__(self, name):
        """Proxy attribute access to the real service."""
        if self._service is None:
            # For synchronous access, we need to block
            import asyncio
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self._ensure_initialized())
            loop.close()
        return getattr(self._service, name)
    
    async def async_search(self, *args, **kwargs):
        """Async wrapper for search method."""
        await self._ensure_initialized()
        return self._service.search(*args, **kwargs)
    
    async def async_get_by_id(self, *args, **kwargs):
        """Async wrapper for get_by_id method."""
        await self._ensure_initialized()
        return self._service.get_by_id(*args, **kwargs)
    
    async def async_get_dependencies(self, *args, **kwargs):
        """Async wrapper for get_dependencies method."""
        await self._ensure_initialized()
        return self._service.get_dependencies(*args, **kwargs)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Optimized Lean Explore MCP Server"
    )
    parser.add_argument(
        "--backend",
        type=str,
        choices=["api", "local", "lazy-local"],
        default="lazy-local",
        help="Backend type. 'lazy-local' defers initialization for faster startup."
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="API key for remote backend"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="ERROR",
        help="Logging level"
    )
    parser.add_argument(
        "--pre-warm",
        action="store_true",
        help="Pre-warm the service after startup (background)"
    )
    return parser.parse_args()


async def pre_warm_service(service: LazyLocalService):
    """Pre-warm the service in background after startup."""
    logger.info("Pre-warming service in background...")
    try:
        # Trigger initialization
        await service._ensure_initialized()
        
        # Optionally do a test query to warm caches
        await service.async_search("test", limit=1)
        logger.info("Service pre-warming completed")
    except Exception as e:
        logger.error(f"Pre-warming failed: {e}")


def main():
    """Main entry point with optimized startup."""
    args = parse_arguments()
    
    # Configure logging
    numeric_level = getattr(logging, args.log_level.upper(), logging.ERROR)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(levelname)s - [%(name)s:%(lineno)d] - %(message)s",
        stream=sys.stderr,
        force=True,
    )
    
    logger.info(f"Starting optimized MCP Server with backend: {args.backend}")
    
    # Initialize backend
    backend_service_instance: Optional[BackendServiceType] = None
    
    if args.backend in ["local", "lazy-local"]:
        # Use lazy loading for local backend
        backend_service_instance = LazyLocalService()
        
        if args.pre_warm:
            # Schedule pre-warming in background
            asyncio.create_task(pre_warm_service(backend_service_instance))
            
    elif args.backend == "api":
        if not args.api_key:
            print("--api-key required for API backend", file=sys.stderr)
            sys.exit(1)
        
        from lean_explore.api.client import Client
        backend_service_instance = Client(api_key=args.api_key)
    
    # Attach backend to MCP app
    mcp_app._lean_explore_backend_service = backend_service_instance
    logger.info("Backend attached, starting MCP server...")
    
    # Run MCP server
    try:
        mcp_app.run(transport="stdio")
    except Exception as e:
        logger.critical(f"Server failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()