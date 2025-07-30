#!/usr/bin/env python3
"""Preload script to warm up MCP server components.

Run this script to pre-initialize heavy components like embedding models
and FAISS indices, reducing startup time for the actual MCP server.
"""

import sys
import time
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lean_explore.mcp.cached_loader import preload_all_assets, get_load_statistics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """Preload all assets and report statistics."""
    logger.info("Starting MCP asset preloading...")
    start_time = time.time()
    
    try:
        # Preload all assets
        preload_all_assets()
        
        # Get statistics
        stats = get_load_statistics()
        
        logger.info("Preloading completed successfully!")
        logger.info("Load times:")
        for component, load_time in stats.items():
            logger.info(f"  {component}: {load_time:.2f}s")
        
        total_time = time.time() - start_time
        logger.info(f"Total preload time: {total_time:.2f}s")
        
    except Exception as e:
        logger.error(f"Preloading failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()