# Codex Claude Peer Review

Codex Claude Peer Review is a Codex skill for bounded adversarial review between Codex and Claude Code. It helps turn high-risk engineering work into an evidence package, an external challenge review, explicit triage, and a converged final decision.

The skill is designed for situations where model agreement is not enough. The final answer should be grounded in repo state, runtime proof, CI results, logs, browser evidence, or other concrete artifacts.

## Included Files

- `SKILL.md`: the Codex skill instructions.
- `agents/openai.yaml`: display metadata for the Codex skill interface.
- `scripts/check_repo.py`: repository validation for required files and common secret patterns.
- `.github/workflows/validate.yml`: GitHub Actions workflow that runs the validation script.

## When To Use It

Use this skill when a task benefits from an independent challenge pass, including:

- architecture decisions;
- difficult root-cause analysis;
- PR or MR merge judgments;
- release, rollback, or blocker decisions;
- security, data, financial, customer, or operational risk;
- explicit requests for Codex and Claude Code to consult, challenge each other, or converge on evidence.

Do not use it for routine low-risk edits or simple summaries unless a user specifically asks for bilateral review.

## Install

The commands below install the skill into the standard Codex skills directory.

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$CODEX_HOME/skills"
git clone https://github.com/YoshiyukiSakura/codex-claude-peer-review.git "$CODEX_HOME/skills/codex-claude-peer-review"
```

If the skill is already installed, update it with:

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
git -C "$CODEX_HOME/skills/codex-claude-peer-review" pull --ff-only
```

## Verify Installation

Run these checks after installation:

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
test -f "$CODEX_HOME/skills/codex-claude-peer-review/SKILL.md"
test -f "$CODEX_HOME/skills/codex-claude-peer-review/agents/openai.yaml"
python3 "$CODEX_HOME/skills/codex-claude-peer-review/scripts/check_repo.py"
```

## Runtime Requirements

- Codex with local skill support.
- Claude Code CLI for the external review path.
- Kimi CLI is optional and is used only as a fallback when Claude Code is unavailable.

The repository does not include credentials. Do not put API keys, tokens, passwords, private customer data, or other secrets in prompts, commits, issues, or pull requests.

## Local Validation

From the repository root:

```bash
python3 scripts/check_repo.py
```

The script verifies required project files, skill metadata, agent metadata, and common high-risk secret patterns.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
