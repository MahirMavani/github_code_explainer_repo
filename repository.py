import re
import shutil
import tempfile
from pathlib import Path

from git import Repo
from git.exc import GitCommandError, GitError

_GITHUB_RE = re.compile(
    r"^https?://(?:www\.)?github\.com/([^/\s]+)/([^/\s]+)/?$",
    re.IGNORECASE,
)


def validate_github_url(url: str) -> str:
    """Validate a public GitHub repository URL and return its .git URL."""
    url = (url or "").strip()
    match = _GITHUB_RE.fullmatch(url.rstrip("/"))
    if not match:
        raise ValueError(
            "Enter a public GitHub repository URL like "
            "https://github.com/username/repository. "
            "Do not use a /blob/ or /tree/ file/folder URL."
        )
    owner, repo = match.groups()
    repo = repo.removesuffix(".git")
    if not owner or not repo:
        raise ValueError("The GitHub owner and repository name are required.")
    return f"https://github.com/{owner}/{repo}.git"


def clone_repository(url: str) -> str:
    """Shallow-clone a public GitHub repository into a temporary directory."""
    validated = validate_github_url(url)
    temp_dir = Path(tempfile.mkdtemp(prefix="repolens_"))
    destination = temp_dir / "repo"
    try:
        Repo.clone_from(
            validated,
            destination,
            depth=1,
            single_branch=True,
            no_tags=True,
        )
        return str(destination)
    except (GitCommandError, GitError, OSError) as exc:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise RuntimeError(
            "Could not clone that repository. Make sure it is public, exists, "
            "and is a repository URL (not a file URL)."
        ) from exc


def cleanup_repository(repo_path: str | None) -> None:
    """Remove the temporary clone safely."""
    if not repo_path:
        return
    path = Path(repo_path)
    try:
        # repo_path is <temporary-dir>/repo
        shutil.rmtree(path.parent if path.name == "repo" else path, ignore_errors=True)
    except OSError:
        pass
