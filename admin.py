"""
Caregiver-facing admin panel.
Add, edit, and delete words in the personal vocabulary, then rebuild the vector DB.

Run: streamlit run admin.py
"""

import json
import sys
import uuid
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "rag"))
from ingest import ingest_words

WORDS_PATH = Path("data/words.json")
SAMPLE_PATH = Path("data/words.sample.json")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Word Finder — Admin",
    page_icon="⚙️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp { background-color: #f4f4f4; }
    h1 { font-size: 1.8rem !important; }
    .stButton > button { border-radius: 8px !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Helpers ────────────────────────────────────────────────────────────────────

def load_words() -> list[dict]:
    if WORDS_PATH.exists():
        with open(WORDS_PATH, encoding="utf-8") as f:
            return json.load(f)
    if SAMPLE_PATH.exists():
        with open(SAMPLE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_words(words: list[dict]) -> None:
    WORDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(WORDS_PATH, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)


def rebuild_db() -> int:
    return ingest_words()


# ── Session state ──────────────────────────────────────────────────────────────
if "words" not in st.session_state:
    st.session_state.words = load_words()

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("⚙️ Admin — Personal Vocabulary")
st.caption("Add, edit, and delete words. Click **Save & Rebuild** when done.")

# ── Rebuild button ─────────────────────────────────────────────────────────────
col_save, col_count = st.columns([1, 3])
with col_save:
    if st.button("💾 Save & Rebuild", type="primary", use_container_width=True):
        save_words(st.session_state.words)
        with st.spinner("Rebuilding vector database…"):
            try:
                count = rebuild_db()
                st.success(f"Done — {count} words in the database.")
            except Exception as e:
                st.error(f"Rebuild failed: {e}")

with col_count:
    st.markdown(
        f"<p style='padding-top:0.6rem;color:#666;'>{len(st.session_state.words)} words loaded</p>",
        unsafe_allow_html=True,
    )

st.divider()

# ── Add new word form ──────────────────────────────────────────────────────────
with st.expander("➕ Add a new word", expanded=False):
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        new_word = c1.text_input("Word *", placeholder="synagogue")
        new_category = c2.text_input("Category", placeholder="places")
        new_desc = st.text_input("Description *", placeholder="the place we go Saturday morning")
        new_notes = st.text_input("Notes", placeholder="near the pharmacy on Herzl Street")
        new_tags = st.text_input("Tags (comma-separated)", placeholder="religion, routine")

        submitted = st.form_submit_button("Add word")
        if submitted:
            if not new_word.strip() or not new_desc.strip():
                st.error("Word and Description are required.")
            else:
                entry = {
                    "id": str(uuid.uuid4()),
                    "word": new_word.strip(),
                    "description": new_desc.strip(),
                    "category": new_category.strip(),
                    "notes": new_notes.strip(),
                    "tags": [t.strip() for t in new_tags.split(",") if t.strip()],
                }
                st.session_state.words.append(entry)
                st.success(f"Added '{new_word}'. Click Save & Rebuild to make it searchable.")

st.divider()

# ── Word list ──────────────────────────────────────────────────────────────────
st.subheader("Vocabulary")

# Filter
search = st.text_input("🔍 Filter words", placeholder="Search by word, description, or category…")
filtered = [
    w for w in st.session_state.words
    if not search
    or search.lower() in w.get("word", "").lower()
    or search.lower() in w.get("description", "").lower()
    or search.lower() in w.get("category", "").lower()
]

if not filtered:
    st.info("No words yet. Add one above." if not search else "No matches.")

for entry in filtered:
    eid = entry["id"]
    with st.container():
        col_word, col_cat, col_desc, col_edit, col_del = st.columns([2, 1.5, 4, 0.7, 0.7])

        col_word.markdown(f"**{entry['word']}**")
        col_cat.markdown(f"<span style='color:#888;font-size:0.9rem;'>{entry.get('category','')}</span>", unsafe_allow_html=True)
        col_desc.markdown(f"<span style='font-size:0.95rem;'>{entry.get('description','')}</span>", unsafe_allow_html=True)

        if col_edit.button("✏️", key=f"edit_{eid}", help="Edit"):
            st.session_state.edit_id = eid if st.session_state.edit_id != eid else None
            st.rerun()

        if col_del.button("🗑️", key=f"del_{eid}", help="Delete"):
            st.session_state.words = [w for w in st.session_state.words if w["id"] != eid]
            st.success(f"Removed '{entry['word']}'. Click Save & Rebuild.")
            st.rerun()

        # Inline edit form
        if st.session_state.edit_id == eid:
            with st.form(f"edit_form_{eid}"):
                ec1, ec2 = st.columns(2)
                e_word = ec1.text_input("Word", value=entry.get("word", ""))
                e_cat  = ec2.text_input("Category", value=entry.get("category", ""))
                e_desc  = st.text_input("Description", value=entry.get("description", ""))
                e_notes = st.text_input("Notes", value=entry.get("notes", ""))
                e_tags  = st.text_input("Tags", value=", ".join(entry.get("tags", [])))
                save_edit = st.form_submit_button("Update")
                if save_edit:
                    for w in st.session_state.words:
                        if w["id"] == eid:
                            w.update({
                                "word": e_word.strip(),
                                "category": e_cat.strip(),
                                "description": e_desc.strip(),
                                "notes": e_notes.strip(),
                                "tags": [t.strip() for t in e_tags.split(",") if t.strip()],
                            })
                    st.session_state.edit_id = None
                    st.success("Updated. Click Save & Rebuild.")
                    st.rerun()

        st.markdown("<hr style='margin:4px 0;border-color:#eee;'>", unsafe_allow_html=True)