import json
import uuid
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"
COLLECTION_NAME = "personal_vocab"
DB_PATH = "db"
WORDS_PATH = "data/words.json"


def build_text(entry: dict) -> str:
    """Concatenate all word fields into a single string for embedding."""
    parts = [f"word: {entry['word']}"]
    if entry.get("description"):
        parts.append(f"description: {entry['description']}")
    if entry.get("notes"):
        parts.append(f"notes: {entry['notes']}")
    if entry.get("category"):
        parts.append(f"category: {entry['category']}")
    if entry.get("tags"):
        parts.append(f"tags: {', '.join(entry['tags'])}")
    return ". ".join(parts)


def ingest_words(words_path: str = WORDS_PATH, db_path: str = DB_PATH) -> int:
    """
    Load words from JSON, embed them, and store in ChromaDB.
    Rebuilds the collection from scratch on every call.
    Returns the number of words ingested.

    Designed with a clean interface so this function can later be
    wrapped as an MCP tool (e.g. reload_vocabulary()).
    """
    path = Path(words_path)
    if not path.exists():
        raise FileNotFoundError(f"Words file not found: {path}")

    with open(path, encoding="utf-8") as f:
        entries = json.load(f)

    documents = [
        Document(
            page_content=build_text(entry),
            metadata={
                "word": entry["word"],
                "category": entry.get("category", ""),
                "entry_id": entry.get("id", str(uuid.uuid4())),
            },
        )
        for entry in entries
    ]

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    # Drop and rebuild so the DB always reflects the current words.json
    existing = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=db_path,
    )
    existing.delete_collection()

    Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=db_path,
    )

    return len(documents)


if __name__ == "__main__":
    count = ingest_words()
    print(f"✓ Ingested {count} words into ChromaDB at '{DB_PATH}'.")
