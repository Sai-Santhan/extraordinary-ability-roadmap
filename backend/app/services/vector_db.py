"""Vector database service using ChromaDB for immigration law RAG."""

import logging
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

_client: Optional[chromadb.ClientAPI] = None
_collection: Optional[chromadb.Collection] = None

PERSIST_DIR = str(Path(__file__).parent.parent.parent / "data" / "chromadb")
COLLECTION_NAME = "immigration_law"


def get_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.Client(Settings(
            persist_directory=PERSIST_DIR,
            anonymized_telemetry=False,
        ))
    return _client


def get_collection() -> chromadb.Collection:
    global _collection
    if _collection is None:
        client = get_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_documents(
    texts: list[str],
    metadatas: list[dict],
    ids: list[str],
) -> None:
    collection = get_collection()
    collection.add(documents=texts, metadatas=metadatas, ids=ids)
    logger.info(f"Added {len(texts)} documents to {COLLECTION_NAME}")


def query(
    text: str,
    n_results: int = 5,
    pathway_filter: Optional[str] = None,
) -> list[dict]:
    """Query the vector DB for relevant legal passages.

    Returns list of dicts with 'text', 'metadata', and 'distance' keys.
    """
    collection = get_collection()
    if collection.count() == 0:
        return []

    where_filter = {"pathway": pathway_filter} if pathway_filter else None

    results = collection.query(
        query_texts=[text],
        n_results=n_results,
        where=where_filter,
    )

    docs = []
    for i, doc in enumerate(results["documents"][0]):
        docs.append({
            "text": doc,
            "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
            "distance": results["distances"][0][i] if results["distances"] else 0,
        })
    return docs


def get_stats() -> dict:
    collection = get_collection()
    return {"collection": COLLECTION_NAME, "count": collection.count()}


def is_seeded() -> bool:
    collection = get_collection()
    return collection.count() > 0
