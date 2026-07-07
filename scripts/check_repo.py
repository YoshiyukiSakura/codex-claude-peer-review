#!/usr/bin/env python3
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "SKILL.md",
    "agents/openai.yaml",
    "README.md",
    "LICENSE",
    ".gitignore",
]

SECRET_PATTERNS = {
    "GitHub classic token": re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    "GitHub fine-grained token": re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
    "GitLab token": re.compile(r"glpat-[A-Za-z0-9_-]{20,}"),
    "OpenAI-style key": re.compile(r"sk-[A-Za-z0-9]{20,}"),
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "Private key block": re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----"),
}


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def check_required_files() -> None:
    for relative_path in REQUIRED_FILES:
        path = ROOT / relative_path
        if not path.is_file():
            fail(f"Missing required file: {relative_path}")


def check_skill_metadata() -> None:
    text = read_text("SKILL.md")
    if not text.startswith("---\n"):
        fail("SKILL.md must start with YAML front matter")
    if "name: codex-claude-peer-review" not in text:
        fail("SKILL.md must declare name: codex-claude-peer-review")
    if "description:" not in text:
        fail("SKILL.md must include a description")


def check_agent_metadata() -> None:
    text = read_text("agents/openai.yaml")
    required_fragments = [
        'display_name: "Codex Claude Peer Review"',
        'short_description: "Adversarial Codex/Claude evidence review"',
        "default_prompt:",
    ]
    for fragment in required_fragments:
        if fragment not in text:
            fail(f"agents/openai.yaml missing required fragment: {fragment}")


def check_common_secret_patterns() -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        relative_path = path.relative_to(ROOT)
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                fail(f"{label} matched in {relative_path}")


def main() -> None:
    check_required_files()
    check_skill_metadata()
    check_agent_metadata()
    check_common_secret_patterns()
    print("Repository validation passed")


if __name__ == "__main__":
    main()
