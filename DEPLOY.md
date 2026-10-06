# 3-minute deployment checklist

1. Push this folder to a new GitHub repository.
2. Streamlit Cloud → Create app.
3. Repository: your GitHub repository.
4. Branch: `main`.
5. Main file: `app.py`.
6. Python: `3.12`.
7. Advanced settings → Secrets:

```toml
HF_TOKEN = "hf_your_token_here"
```

8. Deploy.
9. Test with:

`https://github.com/psf/requests`

If the app says Hugging Face authentication is not configured, the secret was not saved correctly.
