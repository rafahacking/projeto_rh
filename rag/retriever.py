import os
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = Path(__file__).parent.parent / "chroma_db"
EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
COLLECTION_NAME = "rh_knowledge"

# Similaridade mínima (0.0–1.0). Abaixo disso, considera sem resposta.
MIN_SIMILARITY = float(os.getenv("RAG_MIN_SIMILARITY", "0.30"))

_collection_cache = None


def _get_collection():
    global _collection_cache
    if _collection_cache is not None:
        return _collection_cache
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL,
        normalize_embeddings=True,
    )
    _collection_cache = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    return _collection_cache


def retrieve(query: str, n_results: int = 4) -> dict:
    """
    Busca os chunks mais relevantes para a query.

    Retorna:
        found      — True se algum chunk passou o limiar de similaridade
        chunks     — lista de {text, meta, similarity}
        sources    — doc_ids únicos encontrados
        top_score  — maior similaridade encontrada (0.0 se nenhum)
    """
    collection = _get_collection()

    if collection.count() == 0:
        return {"found": False, "chunks": [], "sources": [], "top_score": 0.0}

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    chunks, sources = [], []

    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        similarity = round(1.0 - dist, 3)
        if similarity >= MIN_SIMILARITY:
            chunks.append({"text": doc, "meta": meta, "similarity": similarity})
            src = meta.get("doc_id", "")
            if src and src not in sources:
                sources.append(src)

    top_score = chunks[0]["similarity"] if chunks else 0.0

    return {
        "found": bool(chunks),
        "chunks": chunks,
        "sources": sources,
        "top_score": top_score,
    }
