import sys

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"
COLLECTION_NAME = "personal_vocab"
DB_PATH = "db"


def retrieve(query: str, k: int = 3, db_path: str = DB_PATH) -> list[dict]:
    """
    Search the personal vocabulary for words matching the query description.

    Args:
        query: The patient's approximate description, e.g. "the place we go Saturday morning"
        k:     Number of candidates to return (default 3)

    Returns:
        List of dicts with keys: word, category, full_text, score (0–1, higher is better)

    Designed as a clean, self-contained function so it can be wrapped directly
    as an MCP tool: search_personal_vocabulary(query: str) -> list[dict]
    """
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    db = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=db_path,
    )

    results = db.similarity_search_with_relevance_scores(query, k=k)

    return [
        {
            "word": doc.metadata["word"],
            "category": doc.metadata.get("category", ""),
            "full_text": doc.page_content,
            "score": round(score, 3),
        }
        for doc, score in results
    ]


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "the place we go on Saturday morning"
    print(f"Query: '{query}'\n")
    for r in retrieve(query):
        print(f"  [{r['score']:.3f}]  {r['word']}  ({r['category']})")
        print(f"           {r['full_text']}\n")
