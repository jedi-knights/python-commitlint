"""Invoke task definitions for development workflows.

Provides tasks for linting, formatting, testing, building, and releasing
the package, plus auto-installation of the pinned go-semantic-release
binary used by the release workflow locally.
"""

from __future__ import annotations

import platform
import shutil
import tarfile
import urllib.request
from pathlib import Path

from invoke.context import Context
from invoke.tasks import task

ROOT = Path(__file__).resolve().parent

SEMANTIC_RELEASE_VERSION = "v0.10.2"
TOOLS_DIR = ROOT / ".tools"


def _resolve_semantic_release() -> Path:
    """Return the path to a usable semantic-release binary, installing if needed."""
    local = TOOLS_DIR / "semantic-release"
    if local.exists():
        return local
    on_path = shutil.which("semantic-release")
    if on_path:
        return Path(on_path)
    return _install_semantic_release()


def _install_semantic_release() -> Path:
    """Download the pinned go-semantic-release binary into .tools/."""
    os_name = platform.system().lower()
    if os_name not in ("linux", "darwin"):
        raise RuntimeError(f"Unsupported OS for auto-install: {os_name}")

    arch_map = {
        "x86_64": "amd64",
        "amd64": "amd64",
        "arm64": "arm64",
        "aarch64": "arm64",
    }
    machine = platform.machine().lower()
    arch = arch_map.get(machine)
    if not arch:
        raise RuntimeError(f"Unsupported architecture: {machine}")

    version = SEMANTIC_RELEASE_VERSION
    bare = version.lstrip("v")
    archive_name = f"semantic-release_{bare}_{os_name}_{arch}.tar.gz"
    url = (
        f"https://github.com/jedi-knights/go-semantic-release/releases/download/"
        f"{version}/{archive_name}"
    )

    TOOLS_DIR.mkdir(exist_ok=True)
    archive_path = TOOLS_DIR / archive_name
    print(f"Downloading {url}")
    with (
        urllib.request.urlopen(url, timeout=60) as response,  # noqa: S310
        archive_path.open("wb") as out,
    ):
        shutil.copyfileobj(response, out)

    with tarfile.open(archive_path) as tf:
        tf.extract("semantic-release", path=TOOLS_DIR, filter="data")
    archive_path.unlink()

    binary = TOOLS_DIR / "semantic-release"
    binary.chmod(0o755)
    return binary


@task
def clean(c: Context) -> None:
    """Remove build artifacts and caches."""
    patterns = [
        "dist",
        "build",
        "*.egg-info",
        ".pytest_cache",
        ".ruff_cache",
        "htmlcov",
        "coverage.xml",
        ".coverage",
    ]
    for pattern in patterns:
        for path in ROOT.glob(pattern):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            else:
                path.unlink(missing_ok=True)
    for cache in ROOT.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)


@task
def lint(c: Context) -> None:
    """Run ruff lint checks."""
    c.run("uv run ruff check .", pty=True)


@task
def format(c: Context, check: bool = False) -> None:
    """Format code with ruff (use --check to verify only)."""
    suffix = " --check" if check else ""
    c.run(f"uv run ruff format{suffix} .", pty=True)


@task
def lint_commit(c: Context) -> None:
    """Validate the most recent commit message against conventional commits."""
    c.run("git log -1 --pretty=%B | uv run commitlint lint --stdin", pty=True)


@task
def test(c: Context, cov: bool = True, xml: bool = False) -> None:
    """Run the test suite (use --xml to also emit coverage.xml)."""
    cmd = "uv run pytest"
    if cov:
        cmd += " --cov --cov-report=term-missing"
        if xml:
            cmd += " --cov-report=xml"
    c.run(cmd, pty=True)


@task(pre=[clean])
def build(c: Context) -> None:
    """Build the distribution."""
    c.run("uv build", pty=True)


@task
def publish(c: Context) -> None:
    """Upload built distributions to PyPI (requires UV_PUBLISH_TOKEN)."""
    c.run("uv publish", pty=True)


@task
def install_semantic_release(c: Context) -> None:
    """Download the pinned semantic-release binary into .tools/."""
    binary = _install_semantic_release()
    print(f"Installed: {binary}")


@task
def release_dryrun(c: Context) -> None:
    """Preview the next release (auto-installs semantic-release if needed)."""
    binary = _resolve_semantic_release()
    c.run(f"{binary} --dry-run --no-interactive", pty=True)


@task
def ci(c: Context) -> None:
    """Run lint + format check + commit-message lint + tests, mirroring CI."""
    lint(c)
    format(c, check=True)
    lint_commit(c)
    test(c)
