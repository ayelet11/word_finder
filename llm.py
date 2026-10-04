import sys

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from retriever import retrieve

load_dotenv()

LLM_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """You are helping a person with aphasia find a word they cannot remember.
They have described what they mean in their own approximate words.
You have been given a short list of candidate words from their personal vocabulary.

Your job:
1. Pick the word that best matches their description.
2. Write a single short, warm confirmation — maximum 8 words, simple language.
   Example: "Yes — the synagogue, where you go on Saturdays."

Respond in this exact format:
WORD: <the word>
EXPLANATION: <your short confirmation>"""


def find_word(query: str, k: int = 3) -> dict:
    """
    Full RAG pipeline: retrieve candidates, then use LLM to pick and explain the best match.

    Args:
        query: The patient's approximate description
        k:     Number of candidates to retrieve before reranking

    Returns:
        Dict with keys: word, explanation, candidates (the full retrieval list)

    Clean interface — can be wrapped as an MCP tool: find_word(query: str) -> dict
    """
    candidates = retrieve(query, k=k)

    if not candidates:
        return {
            "word": None,
            "explanation": "I could not find a match. Please ask your caregiver to add more words.",
            "candidates": [],
        }

    candidate_lines = "\n".join(
        f"{i+1}. {c['word']} — {c['full_text']}"
        for i, c in enumerate(candidates)
    )

    human_message = f"""The person typed: "{query}"

Candidates from their personal vocabulary:
{candidate_lines}

Which word did they mean?"""

    llm = ChatOpenAI(model=LLM_MODEL, temperature=0)
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=human_message),
    ])

    word, explanation = _parse_response(response.content, fallback=candidates[0]["word"])

    return {
        "word": word,
        "explanation": explanation,
        "candidates": candidates,
    }


def _parse_response(text: str, fallback: str) -> tuple[str, str]:
    """Parse the LLM's WORD / EXPLANATION response. Degrade gracefully on bad output."""
    word = fallback
    explanation = ""
    for line in text.strip().splitlines():
        if line.startswith("WORD:"):
            word = line.removeprefix("WORD:").strip()
        elif line.startswith("EXPLANATION:"):
            explanation = line.removeprefix("EXPLANATION:").strip()
    return word, explanation


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "the place we go on Saturday morning"
    print(f"Query: '{query}'\n")
    result = find_word(query)
    print(f"→  {result['word']}")
    print(f"   {result['explanation']}\n")
    print("Candidates considered:")
    for c in result["candidates"]:
        print(f"  [{c['score']:.3f}]  {c['word']}")