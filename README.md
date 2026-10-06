# RepoLens AI — GitHub Repository Code Explainer

A Streamlit GenAI mini-project that accepts a **public GitHub repository URL**, shallow-clones it, selects relevant source files, and asks **Qwen 2.5 0.5B Instruct** through Hugging Face Inference to explain the project in simple language.

## Why this version is fast on Streamlit Cloud

This cloud version **does not install PyTorch or download a Transformer model**. It uses Hugging Face hosted inference through `huggingface_hub.InferenceClient`, so Streamlit Cloud only handles repository processing and the web UI.

## Deploy on Streamlit Community Cloud

1. Upload/push this folder to a GitHub repository.
2. In Streamlit Community Cloud, create an app using:
   - Branch: `main`
   - Main file: `app.py`
   - Python: `3.12`
3. Open **Settings → Secrets** and add:

```toml
HF_TOKEN = "hf_your_token_here"
```

The token must have permission to use Hugging Face Inference Providers. Never commit the token to GitHub.

## Run locally

```bash
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
```

Set the token before running, or put it in `.streamlit/secrets.toml`:

```toml
HF_TOKEN = "hf_your_token_here"
```

Then:

```bash
python -m streamlit run app.py
```

## Test repository

```text
https://github.com/psf/requests
```

## Architecture

GitHub Repository → GitPython → Code Processor → Hugging Face Inference → Qwen 2.5 0.5B → Streamlit Explanation

## Important limitation

Only public GitHub repositories are supported. Very large repositories are bounded to a small set of high-value files so the inference request stays fast and affordable.
