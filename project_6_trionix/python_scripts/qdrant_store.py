import os
import hashlib
import logging
import uuid
from typing import List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


# Default to the Qdrant container IP discovered on the current host's Docker bridge network.
# If you run Qdrant and the web app via docker-compose, set QDRANT_URL in the environment instead.
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333/")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
DEFAULT_COLLECTION = os.getenv("QDRANT_COLLECTION", "trionix-transcripts")
DEFAULT_VECTOR_SIZE = int(os.getenv("EMBEDDING_DIM", "384"))
_client_cache = None


def _make_point_id(source_id: str, chunk_index: int) -> str:
    key = f"{source_id}:{chunk_index}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, key))


def get_client() -> QdrantClient:
    global _client_cache
    if _client_cache is not None:
        return _client_cache

    # Try the configured URL first, then fall back to common Docker hostnames
    candidates = [QDRANT_URL]
    # Also try the discovered container IP directly (useful when the web container has QDRANT_URL set to host.docker.internal)
    candidates.append("http://172.17.0.3:6333")
    # Useful on Docker Desktop for host-to-container access
    if "host.docker.internal" not in QDRANT_URL:
        candidates.append("http://host.docker.internal:6333")
    # If Qdrant is running in a container named trionix_qdrant on a user-defined network
    candidates.append("http://trionix_qdrant:6333")

    last_exc = None
    for url in candidates:
        try:
            print(f"Attempting Qdrant client connection to: {url}")
            logger.info("Creating Qdrant client for %s", url)
            client = QdrantClient(url=url, api_key=QDRANT_API_KEY)
            # perform a lightweight operation to verify connectivity
            client.get_collections()
            print(f"Connected to Qdrant at: {url}")
            logger.info("Connected to Qdrant at: %s", url)
            _client_cache = client
            return _client_cache
        except Exception as e:
            last_exc = e
            logger.warning("Qdrant client connection to %s failed: %s", url, e)
            print(f"Qdrant connection to {url} failed: {e}")

    logger.exception("Failed to connect to any Qdrant endpoint. Last error: %s. Falling back to in-memory.", last_exc)
    print("Failed to connect to any Qdrant endpoint. Falling back to in-memory QdrantClient(':memory:')")
    _client_cache = QdrantClient(location=":memory:")
    return _client_cache


def ensure_collection(collection_name: str = DEFAULT_COLLECTION, vector_size: int = DEFAULT_VECTOR_SIZE):
    client = get_client()
    try:
        logger.info("Checking collection '%s' (vector_size=%s)", collection_name, vector_size)
        client.get_collection(collection_name=collection_name)
    except Exception:
        logger.info("Collection '%s' not found, creating...", collection_name)
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        logger.info("Collection '%s' created", collection_name)


def recreate_collection(collection_name: str = DEFAULT_COLLECTION, vector_size: int = DEFAULT_VECTOR_SIZE):
    client = get_client()
    logger.info("Recreating collection '%s' (vector_size=%s)", collection_name, vector_size)
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )
    logger.info("Collection '%s' recreated", collection_name)


def get_source_summary(collection_name: str = DEFAULT_COLLECTION, batch_size: int = 100):
    client = get_client()
    source_ids = set()
    point_count = 0
    offset = None

    try:
        while True:
            points, next_offset = client.scroll(
                collection_name=collection_name,
                limit=batch_size,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )
            point_count += len(points)

            for point in points:
                payload = point.payload or {}
                source_id = payload.get("source_id")
                if source_id:
                    source_ids.add(source_id)

            if next_offset is None:
                break

            offset = next_offset
    except Exception as e:
        logger.info("Could not read source summary for collection '%s': %s", collection_name, e)
        return set(), 0

    return source_ids, point_count


def upsert_points(collection_name: str, points: List[Dict[str, Any]]):
    """Points should be a list of dicts with keys: id (str), vector (List[float]), payload (dict)

    Example:
        points = [
            {"id": "abc", "vector": [...], "payload": {"text": "...", "start": 1.2, "end": 3.4}},
        ]
    """
    client = get_client()
    logger.info("Upserting %d points into collection '%s'", len(points), collection_name)
    point_structs = [PointStruct(id=p["id"], vector=p["vector"], payload=p.get("payload")) for p in points]
    try:
        client.upsert(collection_name=collection_name, points=point_structs)
        logger.info("Upsert completed for collection '%s'", collection_name)
    except Exception as e:
        logger.exception("Upsert failed: %s", e)
        raise


def search(collection_name: str, query_vector: List[float], top: int = 5):
    client = get_client()
    logger.info("Searching collection '%s' top=%d, query_vector_len=%d", collection_name, top, len(query_vector))
    try:
        response = client.query_points(collection_name=collection_name, query=query_vector, limit=top, with_payload=True)
        hits = getattr(response, "points", response)
    except Exception as e:
        logger.exception("Search failed: %s", e)
        raise
    # each hit has .id, .score, .payload
    results = []
    for h in hits:
        results.append({
            "id": h.id,
            "score": h.score,
            "payload": h.payload,
        })
    return results


if __name__ == "__main__":
    # simple smoke test when run directly
    ensure_collection()
    print(f"Collection '{DEFAULT_COLLECTION}' ensured at {QDRANT_URL}")
