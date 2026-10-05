"""
Patient-facing Streamlit app.
Large text, minimal UI, designed for ease of use with aphasia.

Run: streamlit run app.py
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "rag"))
from pathlib import Path
import sys

from ingest import ingest_words

DB_PATH = "db"
if not Path(DB_PATH).exists() or not any(Path(DB_PATH).iterdir()):
    ingest_words()  # builds from data/words.sample.json automatically
from llm import find_word

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Word Finder",
    page_icon="💬",
    layout="centered",
)

# ── Styling: large text, calm colours, big buttons ─────────────────────────────
st.markdown(
    """
    <style>
    .stApp { background-color: #f8f6f2; }
    h1 { font-size: 2.2rem !important; color: #2c2c2c; }
    .result-box {
        background: #ffffff;
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-top: 1.5rem;
        border: 2px solid #d4e8d0;
        text-align: center;
    }
    .result-word {
        font-size: 3rem;
        font-weight: 700;
        color: #2a6e3f;
        letter-spacing: 0.02em;
    }
    .result-explanation {
        font-size: 1.4rem;
        color: #555;
        margin-top: 0.5rem;
    }
    .stTextArea textarea {
        font-size: 1.3rem !important;
        border-radius: 12px !important;
    }
    .stButton > button {
        font-size: 1.3rem !important;
        padding: 0.75rem 2.5rem !important;
        border-radius: 12px !important;
        background-color: #2a6e3f !important;
        color: white !important;
        border: none !important;
        width: 100%;
    }
    .stButton > button:hover { background-color: #225733 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── UI ─────────────────────────────────────────────────────────────────────────
st.title("💬 Word Finder")
st.markdown(
    "<p style='font-size:1.2rem;color:#666;'>Describe what you mean — I will find the word.</p>",
    unsafe_allow_html=True,
)

query = st.text_area(
    label="What are you thinking of?",
    placeholder="e.g.  the place we go on Saturday morning",
    height=120,
    label_visibility="visible",
)

if st.button("Find the word"):
    if not query.strip():
        st.warning("Please type a description first.")
    else:
        with st.spinner("Looking…"):
            try:
                result = find_word(query.strip())
            except FileNotFoundError:
                st.error(
                    "No words loaded yet. Ask your caregiver to open the Admin panel "
                    "and add some words first."
                )
                st.stop()
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.stop()

        if result["word"]:
            st.markdown(
                f"""
                <div class="result-box">
                    <div class="result-word">{result['word']}</div>
                    <div class="result-explanation">{result['explanation']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander("Other possibilities"):
                for c in result["candidates"]:
                    st.markdown(f"- **{c['word']}** &nbsp; _{c['category']}_")
        else:
            st.info("No match found. Try describing it differently.")

st.markdown("---")
st.markdown(
    "<p style='font-size:0.9rem;color:#aaa;text-align:center;'>"
    "Caregiver? <a href='/admin' target='_self'>Open Admin panel</a></p>",
    unsafe_allow_html=True,
)
