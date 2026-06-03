import os
import hashlib
import logging
from typing import List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
DEFAULT_COLLECTION = os.getenv("QDRANT_COLLECTION", "trionix-transcripts")
DEFAULT_VECTOR_SIZE = int(os.getenv("EMBEDDING_DIM", "384"))


def _make_point_id(source_id: str, chunk_index: int) -> str:
    key = f"{source_id}:{chunk_index}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()


def get_client() -> QdrantClient:
    logger.info("Creating Qdrant client for %s", QDRANT_URL)
    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        return client
    except Exception as e:
        logger.exception("Failed to create Qdrant client: %s", e)
        raise


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
        hits = client.search(collection_name=collection_name, query_vector=query_vector, limit=top)
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
