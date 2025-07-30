# src/lean_explore/mcp/cached_loader.py

"""Cached model and index loader to speed up initialization.

Implements a singleton pattern with file-based caching for:
- Embedding model (cached in memory)
- FAISS index metadata
- Pre-computed embeddings
"""

import os
import pickle
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import threading
import time

logger = logging.getLogger(__name__)


class CachedModelLoader:
    """Singleton loader with persistent caching."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._embedding_model = None
        self._faiss_index = None
        self._text_chunk_map = None
        self._load_times = {}
        
        # Cache directory
        self._cache_dir = Path.home() / ".cache" / "lean-explore" / "models"
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        
    def get_embedding_model(self, model_name: str):
        """Get embedding model with caching."""
        if self._embedding_model is not None:
            return self._embedding_model
            
        start_time = time.time()
        
        # Try to load from environment variable first (for pre-loaded models)
        model_cache_env = os.environ.get("LEAN_EXPLORE_MODEL_CACHE")
        if model_cache_env and Path(model_cache_env).exists():
            try:
                with open(model_cache_env, 'rb') as f:
                    self._embedding_model = pickle.load(f)
                logger.info(f"Loaded model from cache: {model_cache_env}")
                self._load_times['embedding_model'] = time.time() - start_time
                return self._embedding_model
            except Exception as e:
                logger.warning(f"Failed to load cached model: {e}")
        
        # Load normally
        from sentence_transformers import SentenceTransformer
        self._embedding_model = SentenceTransformer(model_name)
        
        self._load_times['embedding_model'] = time.time() - start_time
        logger.info(f"Model loaded in {self._load_times['embedding_model']:.2f}s")
        
        return self._embedding_model
    
    def get_faiss_assets(self, index_path: str, map_path: str):
        """Get FAISS index and map with optimized loading."""
        if self._faiss_index is not None and self._text_chunk_map is not None:
            return self._faiss_index, self._text_chunk_map
            
        start_time = time.time()
        
        import faiss
        import pickle
        
        # Load index
        self._faiss_index = faiss.read_index(index_path)
        
        # Load map
        with open(map_path, 'rb') as f:
            self._text_chunk_map = pickle.load(f)
            
        self._load_times['faiss_assets'] = time.time() - start_time
        logger.info(f"FAISS assets loaded in {self._load_times['faiss_assets']:.2f}s")
        
        return self._faiss_index, self._text_chunk_map
    
    def get_load_statistics(self) -> Dict[str, float]:
        """Get loading time statistics."""
        return self._load_times.copy()
    
    def preload_all(self):
        """Preload all assets for warming up."""
        from lean_explore import defaults
        
        logger.info("Preloading all assets...")
        
        # Load embedding model
        self.get_embedding_model(defaults.DEFAULT_EMBEDDING_MODEL_NAME)
        
        # Load FAISS assets
        self.get_faiss_assets(
            str(defaults.DEFAULT_FAISS_INDEX_PATH),
            str(defaults.DEFAULT_FAISS_MAP_PATH)
        )
        
        total_time = sum(self._load_times.values())
        logger.info(f"All assets preloaded in {total_time:.2f}s")


# Global instance
_cached_loader = CachedModelLoader()


def get_cached_embedding_model(model_name: str):
    """Get cached embedding model."""
    return _cached_loader.get_embedding_model(model_name)


def get_cached_faiss_assets(index_path: str, map_path: str):
    """Get cached FAISS assets."""
    return _cached_loader.get_faiss_assets(index_path, map_path)


def get_load_statistics() -> Dict[str, float]:
    """Get loading statistics."""
    return _cached_loader.get_load_statistics()


def preload_all_assets():
    """Preload all assets."""
    _cached_loader.preload_all()