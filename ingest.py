'''
Run whenever you update words.json.
It builds the text string that gets embedded from all fields combined,
drops and rebuilds the ChromaDB collection cleanly, and prints a confirmation.

Set env key for OPEN AI: Missing credentials. Please pass an `api_key`, `workload_identity`, `admin_api_key`, or set the `OPENAI_API_KEY` or `OPENAI_ADMIN_KEY` environment variable.
'''
import truststore

truststore.inject_into_ssl()
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
r'''

from openai import OpenAI

client = OpenAI()

raceback (most recent call last):
  File "C:\Program Files\JetBrains\PyCharm 2025.3.3\plugins\python-ce\helpers\pydev\pydevconsole.py", line 364, in runcode
    coro = func()
           ^^^^^^
  File "<input>", line 1, in <module>
  File "C:\Program Files\JetBrains\PyCharm 2025.3.3\plugins\python-ce\helpers\pydev\_pydev_bundle\pydev_umd.py", line 197, in runfile
    pydev_imports.execfile(filename, global_vars, local_vars)  # execute the script
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Program Files\JetBrains\PyCharm 2025.3.3\plugins\python-ce\helpers\pydev\_pydev_imps\_pydev_execfile.py", line 18, in execfile
    exec(compile(contents+"\n", file, 'exec'), glob, loc)
  File "C:\Users\User\Documents\Ayelet\LLM Projects\WordFinder\ingest.py", line 87, in <module>
    count = ingest_words()
            ^^^^^^^^^^^^^^
  File "C:\Users\User\Documents\Ayelet\LLM Projects\WordFinder\ingest.py", line 66, in ingest_words
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\User\Documents\Ayelet\LLM Projects\WordFinder\.venv\Lib\site-packages\pydantic\main.py", line 263, in __init__
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\User\Documents\Ayelet\LLM Projects\WordFinder\.venv\Lib\site-packages\langchain_openai\embeddings\base.py", line 454, in validate_environment
    self.async_client = openai.AsyncOpenAI(
                        ^^^^^^^^^^^^^^^^^^^
  File "C:\Users\User\Documents\Ayelet\LLM Projects\WordFinder\.venv\Lib\site-packages\openai\_client.py", line 1019, in __init__
    raise OpenAIError(
openai.OpenAIError: Missing credentials. Please pass an `api_key`, `workload_identity`, `admin_api_key`, or set the `OPENAI_API_KEY` or `OPENAI_ADMIN_KEY` environment variable.


'''