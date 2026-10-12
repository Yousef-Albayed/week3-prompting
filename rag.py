"""RAG — policy-grounded answers.

Task: answer a customer question using ONLY the retrieved help-center text. If the
answer isn't in the docs, the model must say it doesn't know (don't hallucinate).

Fill in YOUR_SYSTEM_PROMPT and YOUR_RETRIEVER.
Run:  python rag.py
"""
import os

from ollama import chat

MODEL = "llama3.1:8b"
DATA = os.path.join(os.path.dirname(__file__), "data", "help_center.txt")


def load_chunks() -> list[str]:
    with open(DATA, encoding="utf-8") as f:
        # one chunk per non-empty line
        return [line.strip() for line in f if line.strip()]


# TODO: return the subset of chunks relevant to `question` (simple keyword overlap is fine).
def YOUR_RETRIEVER(question: str, chunks: list[str]) -> list[str]:
    import re
    stop_words = {"how", "long", "do", "i", "have", "to", "an", "the", "a", "is", "are", "what", "whats", "what's", "your", "you"}
    words = [w.lower() for w in re.findall(r"\w+", question) if w.lower() not in stop_words and len(w) > 1]

    relevant = []
    for chunk in chunks:
        chunk_lower = chunk.lower()
        for w in words:
            prefix = w[:7] if len(w) >= 7 else w
            if w in chunk_lower or prefix in chunk_lower:
                relevant.append(chunk)
                break
    return relevant


# TODO: Fill this in! Force the model to answer only from the provided context.
YOUR_SYSTEM_PROMPT = """You are a helpful customer support assistant. Answer the user's question using ONLY the facts provided in the Context.
If the answer is not contained in the Context, you MUST explicitly state that you do not know (e.g., "I do not know"). Never hallucinate or assume facts not present in the Context."""

CASES = [
    ("How long do I have to return an item?", ["30 days"]),
    ("Do you ship internationally?", ["international"]),
    ("What's your CEO's home address?", ["don't know", "do not know", "not sure", "cannot"]),
]


def answer(question: str) -> str:
    context = "\n".join(YOUR_RETRIEVER(question, load_chunks()))
    resp = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": YOUR_SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        options={"temperature": 0.0},
    )
    return resp.message.content.strip().lower()


def run() -> bool:
    passed = 0
    for question, needles in CASES:
        got = answer(question)
        ok = any(n.lower() in got for n in needles)
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] {question!r} -> {got[:80]!r}")
    print(f"{passed}/{len(CASES)} correct")
    return passed == len(CASES)


if __name__ == "__main__":
    run()
