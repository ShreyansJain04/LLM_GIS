# Tutoring Assistant

This project contains a small command-line tutoring assistant. It keeps a
JSON profile per user and can run in **learn**, **review** or **test** mode.

```
python main.py
```

Set the environment variable `OPENAI_API_KEY` if you want to query OpenAI.
Without it, stub responses will be returned.

The planner is implemented as an agent that queries the domain expert LLM to
create learning plans and drive teaching loops. The domain expert includes a
minimal retrieval step that pulls text snippets from the `docs/` directory and
injects them into prompts (a lightweight RAG approach). If no API key is
provided or parsing fails, defaults from `topics.json` are used.
