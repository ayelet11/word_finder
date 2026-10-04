# Word-Finding Assistant — Project Context

## What this is
A RAG app that helps adults with aphasia retrieve words from a personal vocabulary.
A caregiver pre-loads words; the patient types an approximate description and gets the word back.
Portfolio project #1 in a learning ladder toward an agentic Hebrew Legal Aid chatbot.

## Stack
- Python 3.11+, LangChain, ChromaDB (local), OpenAI (`text-embedding-3-small`, `gpt-4o-mini`)
- Streamlit UI, deployed to Streamlit Cloud

## Key files
| File | Purpose |
|---|---|
| `rag/ingest.py` | Load `words.json` → embed → store in ChromaDB. Run once per vocabulary update. |
| `rag/retriever.py` | `retrieve(query, k)` → top-k matching words. Core RAG function. Future MCP tool. |
| `rag/llm.py` | `find_word(query)` → rerank candidates + short warm explanation via gpt-4o-mini. |
| `app.py` | Patient-facing Streamlit UI. Large text, minimal controls, calm design. |
| `admin.py` | Caregiver Streamlit panel — add / edit / delete words + rebuild vector DB in one click. |
| `data/words.json` | Personal vocabulary — do NOT commit (private data, in .gitignore). |
| `data/words.sample.json` | Sample data with 8 entries, safe to commit. Copy to words.json to get started. |
| `db/` | ChromaDB persisted files — do not commit (in .gitignore, rebuild with ingest.py). |

## Current status
- [x] `rag/ingest.py` — done
- [x] `rag/retriever.py` — done
- [x] `rag/llm.py` — done
- [x] `app.py` — done
- [x] `admin.py` — done
- [ ] Deploy to Streamlit Cloud — next

## Running locally
```bash
cp data/words.sample.json data/words.json   # first time only
pip install -r requirements.txt
python rag/ingest.py                         # build vector DB
streamlit run app.py                         # patient UI  (localhost:8501)
streamlit run admin.py                       # caregiver UI (localhost:8501)
```

## Data schema (`words.json` entries)
```json
{
  "id": "uuid",
  "word": "synagogue",
  "description": "the place we go Saturday morning",
  "category": "places",
  "notes": "near the old pharmacy on Herzl Street",
  "tags": ["religion", "routine"]
}
```
The embedded text is all fields concatenated: `word + description + notes + category + tags`.

## Design principles
- `retrieve()` in `retriever.py` is a **clean standalone function** — no LangChain chain wrapping.
  It will be exposed as an MCP tool in the next project (Hebrew Legal Aid agentic system).
  Keep this interface stable: `retrieve(query: str, k: int) -> list[dict]`.
- `find_word()` in `llm.py` is also MCP-ready: `find_word(query: str) -> dict`.
- Admin panel rebuilds the DB in-process (calls `ingest_words()` directly) — no separate script needed.
- `words.json` is excluded from git; `words.sample.json` is the shareable demo dataset.

## Next project: Hebrew Legal Aid chatbot
`retrieve()` and `find_word()` transfer directly — same pattern, bigger corpus.
Changes needed: PDF loader, larger chunk size, citation layer, Pinecone instead of ChromaDB.