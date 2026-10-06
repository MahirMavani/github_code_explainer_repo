import os
from functools import lru_cache

from huggingface_hub import InferenceClient

MODEL = os.getenv("HF_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")

SYSTEM_PROMPT = """You are RepoLens AI, a software-project explainer for college students.
Analyze only the repository context supplied by the user. Do not invent features.
Do not reproduce source code. Explain the actual project in simple, accurate language.
Keep the answer concise enough for a web app and use the exact headings requested."""


def build_prompt(repository_context: str) -> str:
    return f"""Analyze this GitHub repository context.

Return exactly these sections:

# Project Overview
Explain what the project is, the problem it solves, and what it is used for in 3-5 sentences.

# Main Features
Give the major features as bullet points.

# Project Structure
Explain the most important files/folders and their purpose. Do not list every generated or test file.

# How the Application Works
Explain the actual end-to-end flow from input to output using the repository evidence.

# Technologies Used
List programming languages, frameworks, libraries, databases, APIs, and important tools that are actually visible.

# Important Code Components
Explain the important modules, functions, classes, or components and their roles. Do not reproduce code.

# Simple Summary
Give 5-8 beginner-friendly sentences summarizing the project.

Repository context:
{repository_context}
"""


@lru_cache(maxsize=1)
def _client(token: str) -> InferenceClient:
    return InferenceClient(provider="auto", api_key=token)


def _get_token() -> str:
    # Environment variable first, then Streamlit secrets if available.
    token = os.getenv("HF_TOKEN", "").strip()
    if token:
        return token
    try:
        import streamlit as st
        token = str(st.secrets.get("HF_TOKEN", "")).strip()
    except Exception:
        token = ""
    return token


def explain_repository(repository_context: str) -> str:
    token = _get_token()
    if not token:
        raise RuntimeError(
            "Hugging Face authentication is not configured. Add HF_TOKEN in "
            "Streamlit Cloud → Settings → Secrets."
        )

    try:
        response = _client(token).chat_completion(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_prompt(repository_context)},
            ],
            max_tokens=750,
            temperature=0.1,
        )
    except Exception as exc:
        message = str(exc)
        if len(message) > 300:
            message = message[:300] + "..."
        raise RuntimeError(f"Hugging Face inference failed: {message}") from exc

    try:
        text = response.choices[0].message.content.strip()
    except (AttributeError, IndexError, TypeError) as exc:
        raise RuntimeError("The AI service returned an unexpected response.") from exc

    if not text:
        raise RuntimeError("The AI service returned an empty explanation.")
    return text
