"""
Builds the dynamic system prompt from user memory context and
retrieved RAG document context.
"""

BASE_PROMPT = """You are a helpful AI assistant that answers questions strictly \
based on a provided document. Your responses are shown as text chat messages, so:
- You may use markdown formatting (lists, bold, headers) where it aids clarity.
- Be clear and well-organized, but not unnecessarily long.
- Match the user's conversational tone."""

GROUNDING_INSTRUCTIONS = """
You must answer only using the "Document context" provided below. \
Do not use outside knowledge, even if you know the answer. \
If the answer is not contained in the document context, say clearly that the \
document doesn't contain that information — do not guess or make anything up. \
When useful, reference which numbered source (e.g. [1], [2]) supports your answer."""

NO_CONTEXT_INSTRUCTIONS = """
No relevant document context was found for this question. \
Tell the user you don't have information on that in the currently loaded document, \
and ask if they'd like to upload a different PDF or rephrase their question."""


def build_system_prompt(
    memories: list[dict],
    emotion_label: str = "calm",
    rag_context: str = "",
    rag_source: str = "none",
) -> str:
    prompt = BASE_PROMPT

    if emotion_label in ("frustrated", "stressed"):
        prompt += "\n- The user seems stressed. Be extra calm, brief, and supportive."
    elif emotion_label == "excited":
        prompt += "\n- The user sounds upbeat. Match their energy."

    if memories:
        facts = "\n".join(f"- {m['text']}" for m in memories)
        prompt += f"\n\nThings you know about this user:\n{facts}"

    if rag_context:
        source_label = "the user's uploaded document" if rag_source == "upload" else "the default document"
        prompt += GROUNDING_INSTRUCTIONS
        prompt += f"\n\nDocument context (from {source_label}):\n{rag_context}"
    else:
        prompt += NO_CONTEXT_INSTRUCTIONS

    return prompt