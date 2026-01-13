import re
from .knowledge_base import DOCUMENTS


def tokenize(text: str) -> set[str]:
    """Simple tokenizer that splits by non-alphanumeric characters and lowercases."""
    return set(re.findall("\\w+", text.lower()))


def calculate_similarity(query_tokens: set[str], doc_tokens: set[str]) -> float:
    """Calculates Jaccard similarity coefficient between query and document tokens."""
    intersection = query_tokens.intersection(doc_tokens)
    union = query_tokens.union(doc_tokens)
    if not union:
        return 0.0
    return len(intersection) / len(union)


def retrieve_documents(query: str, top_k: int = 3) -> list[dict]:
    """Retrieves the most relevant documents based on keyword similarity."""
    query_tokens = tokenize(query)
    scored_docs = []
    for doc in DOCUMENTS:
        doc_text = f"{doc['title']} {doc['content']} {' '.join(doc['keywords'])}"
        doc_tokens = tokenize(doc_text)
        base_score = calculate_similarity(query_tokens, doc_tokens)
        title_tokens = tokenize(doc["title"])
        title_boost = 0.2 if query_tokens.intersection(title_tokens) else 0.0
        final_score = base_score + title_boost
        if final_score > 0:
            scored_docs.append((final_score, doc))

    def get_score(item):
        return item[0]

    scored_docs.sort(key=get_score, reverse=True)
    return [item[1] for item in scored_docs[:top_k]]


def format_context(docs: list[dict]) -> str:
    """Formats retrieved documents into a string for the LLM prompt."""
    if not docs:
        return "No specific documentation found for this query."
    context_parts = []
    for i, doc in enumerate(docs, 1):
        context_parts.append(f"Source {i} ({doc['title']}):\n{doc['content']}")
    return """

""".join(context_parts)