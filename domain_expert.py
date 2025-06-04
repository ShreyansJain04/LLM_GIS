"""OpenAI wrapper with a tiny RAG helper."""
import os
from pathlib import Path

try:  # pragma: no cover - library might not be installed in tests
    import openai
except ImportError:  # pragma: no cover - fall back to stubs
    openai = None

MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
DOCUMENTS_PATH = Path('docs')


def _retrieve_context(topic: str) -> str:
    """Very small retrieval helper that concatenates text files containing the topic."""
    context_parts = []
    if DOCUMENTS_PATH.exists():
        for path in DOCUMENTS_PATH.glob('*.txt'):
            text = path.read_text()
            if topic.lower() in text.lower():
                context_parts.append(text.strip())
    return '\n'.join(context_parts)


def query_domain_expert(prompt: str, context: str = "") -> str:
    if context:
        prompt = f"Use the following context to answer:\n{context}\n\n{prompt}"
    if openai is None:
        return f"[Stubbed response for prompt: {prompt[:40]}...]"
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY not set')
    openai.api_key = api_key
    resp = openai.ChatCompletion.create(
        model=MODEL,
        messages=[{'role': 'user', 'content': prompt}],
    )
    return resp.choices[0].message['content']


def explain_concept(topic: str) -> str:
    prompt = f"Explain the concept of {topic} in simple terms."
    context = _retrieve_context(topic)
    return query_domain_expert(prompt, context)


def generate_example(topic: str) -> str:
    prompt = f"Provide a worked example for {topic}."
    context = _retrieve_context(topic)
    return query_domain_expert(prompt, context)


def generate_question(topic: str) -> str:
    prompt = f"Create a short question on {topic}."
    context = _retrieve_context(topic)
    return query_domain_expert(prompt, context)


def check_answer(question: str, answer: str):
    prompt = (
        f"Question: {question}\nUser answer: {answer}\n"
        "Determine if the answer is correct and explain."
    )
    context = _retrieve_context(question)
    feedback = query_domain_expert(prompt, context)
    correct = 'correct' in feedback.lower()
    return correct, feedback


def generate_summary(topic: str) -> str:
    prompt = f"Give a short summary of {topic}."
    context = _retrieve_context(topic)
    return query_domain_expert(prompt, context)

