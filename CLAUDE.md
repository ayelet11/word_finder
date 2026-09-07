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
| `rag/llm.py` | (not yet built) Rerank + explain candidates using gpt-4o-mini |
| `app.py` | (not yet built) Patient-facing Streamlit UI |
| `admin.py` | (not yet built) Caregiver Streamlit panel to add/edit/delete words |
| `data/words.json` | Personal vocabulary (copy from `words.sample.json` to start) |
| `data/words.sample.json` | Sample data, safe to commit |
| `db/` | ChromaDB persisted files — do not commit (in .gitignore) |

## Current status
- [x] `ingest.py` — done
- [x] `retriever.py` — done
- [ ] `llm.py` — next
- [ ] `app.py` — next
- [ ] `admin.py` — next

## Design principle
`retrieve()` is intentionally a clean, standalone function (not buried in a chain).
It will be wrapped as an MCP tool in a later project (Hebrew Legal Aid agentic system).
Keep this interface stable.

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
The embedded text is: `word + description + notes + category + tags` concatenated.

## Running locally
```bash
cp data/words.sample.json data/words.json
python rag/ingest.py          # build the vector DB
python rag/retriever.py "the place we go Saturday morning"   # test a query
```
