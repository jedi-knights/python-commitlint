"""
Updates the version in pyproject.toml, VERSION, package.json, and package-lock.json.

Usage:
    python3 update_version.py <version>
"""

import argparse
import json
import logging
import re
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def update_pyproject_toml(version: str) -> None:
    path = Path("pyproject.toml")
    content = path.read_text(encoding="utf-8")
    content = re.sub(
        r'^version = ".*"',
        f'version = "{version}"',
        content,
        flags=re.MULTILINE,
    )
    path.write_text(content, encoding="utf-8")
    logging.info("Updated pyproject.toml to version %s", version)


def update_version_file(version: str) -> None:
    path = Path("VERSION")
    path.write_text(version, encoding="utf-8")
    logging.info("Updated VERSION to %s", version)


def update_json_file(path: Path, version: str) -> None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        data["version"] = version
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        logging.info("Updated %s to version %s", path, version)
    except (FileNotFoundError, json.JSONDecodeError) as err:
        logging.warning("Skipping %s: %s", path, err)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update version in project files.")
    parser.add_argument("version", type=str, help="The new version to set")
    args = parser.parse_args()

    update_pyproject_toml(args.version)
    update_version_file(args.version)
    update_json_file(Path("package.json"), args.version)
    update_json_file(Path("package-lock.json"), args.version)
