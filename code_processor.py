from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".c", ".cpp", ".h", ".hpp",
    ".cs", ".go", ".rs", ".php", ".rb", ".swift", ".kt", ".kts",
    ".html", ".css", ".scss", ".sql", ".sh", ".bash", ".json", ".yaml", ".yml",
    ".xml", ".md", ".txt",
}
IGNORED_DIRS = {
    ".git", ".github", ".idea", ".vscode", "node_modules", "venv", ".venv",
    "env", "__pycache__", "dist", "build", "target", "bin", "obj", ".next",
    "coverage", ".pytest_cache", "tests", "test", "docs", "examples",
}
IGNORED_FILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock"}
PRIORITY_NAMES = {
    "README.md": 0, "README": 0, "requirements.txt": 1, "pyproject.toml": 1,
    "package.json": 1, "main.py": 2, "app.py": 2, "server.py": 2, "run.py": 2,
    "index.py": 2, "main.js": 2, "app.js": 2, "server.js": 2, "index.js": 2,
    "main.ts": 2, "app.ts": 2, "server.ts": 2, "index.ts": 2,
}
MAX_FILES = 12
MAX_FILE_CHARS = 3500
MAX_TOTAL_CHARS = 18000


def is_relevant_file(path: Path) -> bool:
    if any(part.lower() in IGNORED_DIRS for part in path.parts):
        return False
    if path.name in IGNORED_FILES:
        return False
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def read_file_safely(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:MAX_FILE_CHARS]
    except (OSError, UnicodeError):
        return ""


def build_repository_context(repo_path: str):
    root = Path(repo_path)
    if not root.exists():
        raise RuntimeError("The cloned repository could not be found.")

    candidates = [p for p in root.rglob("*") if p.is_file() and is_relevant_file(p)]

    def sort_key(path: Path):
        name_score = PRIORITY_NAMES.get(path.name, 5)
        ext_score = 0 if path.suffix.lower() in {".py", ".js", ".ts", ".tsx", ".java", ".go", ".cpp", ".c"} else 1
        return (name_score, ext_score, len(path.parts), str(path).lower())

    candidates.sort(key=sort_key)
    selected, chunks = [], []
    total = 0

    for path in candidates:
        if len(selected) >= MAX_FILES or total >= MAX_TOTAL_CHARS:
            break
        content = read_file_safely(path)
        if not content.strip():
            continue
        rel = path.relative_to(root).as_posix()
        block = f"\n===== FILE: {rel} =====\n{content}\n"
        remaining = MAX_TOTAL_CHARS - total
        if remaining <= 200:
            break
        block = block[:remaining]
        chunks.append(block)
        selected.append(rel)
        total += len(block)

    if not chunks:
        raise RuntimeError("No supported source or documentation files were found.")
    return "".join(chunks), selected
