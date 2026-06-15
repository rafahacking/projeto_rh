import os
import re
from pathlib import Path

import frontmatter
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import MarkdownHeaderTextSplitter

CHROMA_PATH = Path(__file__).parent.parent / "chroma_db"
EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
COLLECTION_NAME = "rh_knowledge"

# Arquivos a ignorar na ingestão
SKIP_FILES = {
    "README.md",
    "source_references.md",
    "GUIDE-001_guia_de_ingestao_chunking_e_testes_de_rag.md",
}


def _get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL,
        normalize_embeddings=True,
    )
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )


def _clean(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def ingest_file(filepath: Path, collection) -> int:
    post = frontmatter.load(str(filepath))
    meta = dict(post.metadata)
    content = _clean(post.content)

    headers_to_split = [("#", "h1"), ("##", "h2"), ("###", "h3")]
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split,
        strip_headers=False,
    )
    chunks = splitter.split_text(content)

    if not chunks:
        return 0

    ids, documents, metadatas = [], [], []
    doc_id = meta.get("doc_id", filepath.stem)

    for i, chunk in enumerate(chunks):
        section = (
            chunk.metadata.get("h2")
            or chunk.metadata.get("h3")
            or chunk.metadata.get("h1")
            or ""
        )
        text = _clean(chunk.page_content)
        if len(text) < 50:
            continue

        tags = meta.get("tags", [])
        ids.append(f"{doc_id}_{i:03d}")
        documents.append(text)
        metadatas.append({
            "doc_id": doc_id,
            "title": meta.get("title", ""),
            "category": meta.get("category", ""),
            "tags": ", ".join(tags) if isinstance(tags, list) else str(tags),
            "section": section,
            "source_file": filepath.name,
            "confidentiality": meta.get("confidentiality", ""),
        })

    if ids:
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    return len(ids)


def ingest_all(docs_path: str | None = None) -> int:
    path = Path(docs_path or os.getenv("RAG_DOCS_PATH", "rag_docs"))

    if not path.exists():
        raise FileNotFoundError(f"Pasta de documentos não encontrada: {path}")

    collection = _get_collection()
    total = 0

    for filepath in sorted(path.glob("**/*.md")):
        if filepath.name in SKIP_FILES:
            continue
        count = ingest_file(filepath, collection)
        print(f"  {filepath.name}: {count} chunks")
        total += count

    final_count = collection.count()
    print(f"\nIngestão concluída — {total} chunks novos | Total na coleção: {final_count}")
    return final_count


if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    load_dotenv()
    path_arg = sys.argv[1] if len(sys.argv) > 1 else None
    ingest_all(path_arg)
