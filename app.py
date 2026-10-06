from pathlib import Path
from urllib.parse import urlparse

import streamlit as st

from code_processor import build_repository_context
from llm import explain_repository
from repository import cleanup_repository, clone_repository, validate_github_url

st.set_page_config(page_title="RepoLens AI", page_icon="◈", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');
html,body,[class*="css"]{font-family:Inter,sans-serif}.stApp{background:radial-gradient(circle at 8% 8%,rgba(139,92,246,.16),transparent 27%),radial-gradient(circle at 92% 12%,rgba(6,182,212,.13),transparent 24%),#070a12}.block-container{max-width:1200px;padding-top:2rem;padding-bottom:4rem}#MainMenu,footer{visibility:hidden}.hero{padding:28px 0 12px}.eyebrow{display:inline-flex;padding:7px 12px;border-radius:999px;color:#c4b5fd;background:rgba(139,92,246,.1);border:1px solid rgba(139,92,246,.25);font-size:12px;font-weight:800}.hero h1{font-family:"Space Grotesk";font-size:clamp(42px,6vw,72px);line-height:.98;letter-spacing:-3px;margin:18px 0;background:linear-gradient(90deg,#fff,#ddd6fe,#67e8f9);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.hero p{max-width:800px;color:#a8b3c7;font-size:16px;line-height:1.7}.card{background:linear-gradient(145deg,rgba(18,25,42,.88),rgba(11,16,29,.76));border:1px solid rgba(148,163,184,.16);border-radius:20px;padding:22px}.metric{background:rgba(15,23,42,.7);border:1px solid rgba(148,163,184,.13);border-radius:16px;padding:18px;min-height:90px}.label{color:#8fa0b8;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.8px}.value{color:#fff;font-family:"Space Grotesk";font-size:23px;font-weight:700;margin-top:5px}.file{padding:11px 13px;margin:6px 0;border-radius:11px;background:rgba(15,23,42,.6);border:1px solid rgba(148,163,184,.1);font:13px ui-monospace,monospace;color:#dbeafe}.stButton>button{height:50px;border:0;border-radius:12px;background:linear-gradient(100deg,#7c3aed,#8b5cf6,#06b6d4);color:white;font-weight:800}.small{color:#8290a7;font-size:12px}.arch{padding:16px;text-align:center;color:#c4b5fd;font-weight:700}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ◈ RepoLens AI")
    st.caption("GitHub repository → code processing → Hugging Face Qwen → explanation")
    st.success("Cloud-ready AI pipeline")
    st.markdown("### Stack")
    st.caption("Python • Streamlit • GitPython")
    st.caption("Hugging Face Inference • Qwen 2.5 0.5B")
    st.markdown("### Deployment")
    st.caption("No PyTorch or local model download is required on Streamlit Cloud.")

st.markdown('''<div class="hero"><div class="eyebrow">✦ GenAI • Developer Tool</div><h1>Understand any<br>repository faster.</h1><p>Paste a public GitHub repository URL. RepoLens AI clones the repository, selects the most useful source files, and asks Qwen to explain the project in beginner-friendly language.</p></div>''', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
github_url = st.text_input("GitHub Repository URL", placeholder="https://github.com/username/repository")
st.caption("Use the repository URL itself — not /blob/main/file.py or /tree/main.")

if st.button("✦  Analyze Repository", type="primary", use_container_width=True):
    url = github_url.strip()
    try:
        validate_github_url(url)
    except ValueError as exc:
        st.error(str(exc))
    else:
        repo_path = None
        try:
            with st.status("Analyzing repository...", expanded=True) as status:
                st.write("1/3 · Cloning repository")
                repo_path = clone_repository(url)
                st.write("2/3 · Selecting relevant source files")
                context, files = build_repository_context(repo_path)
                st.write(f"Selected {len(files)} files. Generating explanation...")
                st.write("3/3 · Asking Qwen through Hugging Face")
                explanation = explain_repository(context)
                status.update(label="Analysis complete", state="complete", expanded=False)
            st.session_state.analysis = {
                "url": url,
                "files": files,
                "explanation": explanation,
            }
        except RuntimeError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")
        finally:
            cleanup_repository(repo_path)

st.markdown('</div>', unsafe_allow_html=True)

result = st.session_state.get("analysis")
if result:
    parsed = urlparse(result["url"])
    parts = [p for p in parsed.path.strip("/").split("/") if p]
    repo_name = parts[1].removesuffix(".git") if len(parts) > 1 else "Repository"
    files = result["files"]
    languages = sorted({Path(f).suffix.lower() for f in files if Path(f).suffix})

    st.markdown("## Repository Intelligence")
    cols = st.columns(4)
    for col, label, value in zip(cols, ["Repository", "Files analyzed", "File types", "AI engine"], [repo_name, len(files), len(languages), "Qwen 2.5"]):
        with col:
            st.markdown(f'<div class="metric"><div class="label">{label}</div><div class="value">{value}</div></div>', unsafe_allow_html=True)

    st.markdown("## Analysis Pipeline")
    st.markdown('<div class="card"><div class="arch">GitHub → GitPython → Code Processor → Hugging Face → Qwen → Explanation</div></div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["✦ AI Explanation", "⌘ Files Analyzed"])
    with tab1:
        st.markdown(result["explanation"])
    with tab2:
        for name in files:
            st.markdown(f'<div class="file">⌁ {name}</div>', unsafe_allow_html=True)
else:
    st.markdown("## Ready to analyze")
    st.info("For your first test, try https://github.com/psf/requests")

st.markdown('<p class="small" style="text-align:center;margin-top:35px">RepoLens AI · Streamlit · GitPython · Hugging Face Inference · Qwen 2.5 0.5B</p>', unsafe_allow_html=True)
