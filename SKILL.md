---
name: codex-claude-peer-review
description: Use when the user explicitly wants Codex and Claude Code to consult, challenge each other, get a second opinion, or converge on high-confidence evidence; also use for high-risk root-cause analysis, architecture decisions, implementation plans, PR/MR merge or blocker judgments, ship or rollback decisions, security/data/operations risk, or prompts mentioning Claude review, Codex review, 会诊, 互审, 双方都有信心, second opinion, or evidence convergence. Do not use for routine low-risk work unless the user asks for bilateral review.
---

# Codex Claude Peer Review

Run a bounded Codex plus Claude Code review loop. Treat the second model as an adversarial reviewer, not as proof. Converge only when evidence resolves the important disagreements or the remaining risk is explicitly recorded.

## Fast Path

1. Classify the request as execution, investigation, decision, or communication.
2. State success criteria before external review: target outcome, reliability requirements, and evidence sources.
3. Build Codex's first pass from real artifacts: repo, diff, runtime, logs, browser state, CI, PR/MR, issue, database, or source material.
4. Send Claude a narrow attack-review request when Codex starts the loop. If Claude already provided the first pass, do not call Claude again.
5. Triage the external review into blockers, material concerns, optional improvements, invalid objections, and residual risks.
6. Gather more evidence only when it can change the decision.
7. Return the converged result with a clear state label: planned, edited, locally tested, browser/runtime verified, CI verified, externally confirmed, blocked, or residual risk accepted.

## Operating Modes

- Codex starts the loop:
  - Inspect the real artifact first.
  - Produce a first-pass plan, diagnosis, implementation summary, or verdict.
  - Send Claude a scoped challenge prompt.
  - If Claude is unavailable after valid invocation attempts, use Kimi fallback and label it clearly.
- Claude or Kimi already provided the first pass:
  - Treat that output as the artifact under review.
  - Attack assumptions, evidence gaps, edge cases, regression risk, overclaims, and weak verification.
  - Do not launch another Claude or Kimi pass from this mode.
- Both sides already responded:
  - Re-check accepted, rejected, and still-open points.
  - Stop when key disagreements are resolved, remaining risks are explicit, or more work needs user authorization.

## Trigger Discipline

- Use proactively only when a wrong answer could create delivery, merge, architecture, security, data, financial, customer, or operational risk.
- Do not spend a peer-review loop on simple summaries, routine edits, low-risk factual answers, or mechanical formatting unless the user asks for it.
- If the user asks for a plan only, review and improve the plan without making code changes.
- If the user asks for execution, keep moving after convergence unless a credential, destructive action, external approval, or unresolved blocker requires user input.

## Evidence Package

Before calling Claude, prepare a compact evidence package with:

- Scope: exact repo, worktree, branch, PR/MR, issue, service, port, URL, database, file, or artifact identifiers.
- User goal: the outcome the user actually asked for.
- Success criteria: what must be true before the answer can be trusted.
- Codex first pass: conclusion plus confidence, or implementation plan plus risk.
- Evidence gathered: commands, tests, logs, screenshots, browser/runtime proof, CI, external state, and file references.
- Known unknowns: facts not yet verified and why they matter.
- Safety constraints: no secrets in prompts, no production mutation unless already authorized, and no unrelated file changes.

Do not paste API keys, tokens, passwords, private customer data, or unnecessary proprietary content into Claude or Kimi prompts. Replace secrets with variable names only, and say that redaction occurred.

## Claude Invocation From Codex

Use the local Claude Code CLI only when Codex starts the loop. Verify current CLI flags with `claude --version` and `claude -p --help` when the environment looks stale, flags fail, or the final answer depends on exact model or permission behavior.

Difficulty routing:

- High difficulty:
  - Request CLI model id `claude-fable-5` with `medium` effort when available.
  - This is the executable high-difficulty route. If the user says `fable 5`, treat that as shorthand for this route, not as a CLI model string.
  - If `claude-fable-5` is unavailable, rerun with `opus` and `xhigh` effort, then report the actual fallback. The current CLI may show the actual model as `claude-opus-4-8`.
  - Use for architecture decisions, difficult root-cause analysis, risky merge/blocker judgments, cross-system workflows, security-sensitive work, and high-impact conclusions.
- Medium difficulty:
  - Request CLI model alias `opus` with `xhigh` effort.
  - This is the executable medium-difficulty route. If the user says `opus 4.8`, treat that as shorthand for this route, not as a CLI model string.
  - Use for normal investigations, implementation review, PR/MR review, localized technical decisions, and moderate-risk plans.
- Low difficulty:
  - Skip Claude unless the user asked for bilateral review or the task becomes riskier than it first appeared.
  - If Claude review is requested for a low-risk task, route it as medium difficulty.

Use one of these command patterns.

Strict no-tool review, preferred when the evidence package fits in the prompt:

```bash
claude -p --verbose --model claude-fable-5 --effort medium --output-format stream-json --include-partial-messages --tools "" --no-session-persistence "$REVIEW_PROMPT"
```

High-difficulty fallback when `claude-fable-5` is unavailable:

```bash
claude -p --verbose --model opus --effort xhigh --output-format stream-json --include-partial-messages --tools "" --no-session-persistence "$REVIEW_PROMPT"
```

Read-only file review, used when Claude must inspect local files:

```bash
claude -p --verbose --model opus --effort xhigh --output-format stream-json --include-partial-messages --tools Read,Grep,Glob --permission-mode plan --no-session-persistence "$REVIEW_PROMPT"
```

Legacy read-only route, used only when the local CLI does not support `--tools` as expected:

```bash
claude -p --verbose --model claude-fable-5 --effort medium --output-format stream-json --include-partial-messages --permission-mode plan --disallowedTools Bash,Edit,Write,NotebookEdit --no-session-persistence "$REVIEW_PROMPT"
```

Rules for invocation:

- Do not pass display strings such as `fable 5` or `opus 4.8` to `--model`; use CLI ids or aliases such as `claude-fable-5` or `opus`.
- Treat model aliases as requests, not guarantees. If the CLI rejects a model, record the rejected alias and the actual fallback command.
- Do not include `MultiEdit` in `--disallowedTools`; this local Claude CLI has rejected that tool name in prior use.
- Prefer `--tools ""` for pure prompt review because it prevents file writes, shell commands, and subagent delegation.
- If Claude requests an out-of-scope tool, tries to write files during read-only review, or launches a subagent that cannot access required evidence, interrupt or stop the run. Treat any partial output as a signal to check, not as a completed peer review.
- Do not imply Claude changed models when the run happened inside an already-open Claude session. Record the actual model/effort if visible; otherwise say it was not verified.

## Kimi Fallback

Use Kimi only when Claude Code is unavailable, fails after valid flags, lacks model access, is blocked by permission/session limits, or remains unavailable after the wait policy.

Kimi fallback command:

```bash
kimi -p "$REVIEW_PROMPT" --output-format stream-json
```

If JSONL streaming is awkward in the shell:

```bash
kimi -p "$REVIEW_PROMPT"
```

Rules for fallback:

- Label the review as `Kimi fallback`.
- Use the same attack-review prompt shape used for Claude.
- Do not claim Codex plus Claude convergence when Kimi was the reviewer.
- Lower confidence unless independent evidence closes the risk.
- Do not combine Kimi prompt mode with `--plan`; this CLI has rejected that combination.
- If both Claude and Kimi are unavailable, stop and report that independent review could not be completed.

## Long-Running Review Handling

- Do not treat 3 to 5 minutes of silence as a hang.
- For high-difficulty review, wait at least 10 minutes before considering the run stalled.
- For very large diffs, architecture reviews, and `xhigh` effort runs, 10 to 20 minutes can still be normal.
- Prefer streaming output and poll the same shell session. Do not start duplicate Claude runs for the same review.
- Abort early only on explicit CLI errors, invalid flags, permission failure, out-of-scope tool use, user cancellation, or clear evidence that the run cannot access the needed artifacts.
- If there is no useful output after the wait window, say `Claude review still pending or stalled`; do not present it as completed peer review.

## Review Prompt Shape

Use direct field labels instead of broad requests:

```text
You are the independent reviewer in a Codex plus Claude Code peer-review loop.

Task: summarize the user's goal in one sentence.
Difficulty: high, medium, or low.
Codex first pass: state the current plan, implementation summary, diagnosis, or verdict.
Evidence gathered: list exact commands, files, logs, browser/runtime proof, CI, screenshots, or external state already checked.
Known unknowns: list uncertain facts and why they matter.
Tool boundary: do not edit files, do not write plan files, do not run shell commands, and do not spawn subagents unless explicitly allowed in this prompt.

Please attack this result. Focus on missing evidence, wrong assumptions, edge cases, regression risks, overclaims, better alternatives, and verification gaps. Separate blockers from material concerns and optional improvements. Do not rewrite the answer unless rewriting exposes a concrete flaw.
```

If Claude must read local files, add exact allowed paths and keep the tool boundary limited to `Read`, `Grep`, and `Glob`.

## Reviewer Response Triage

- Blocker: would change a merge, ship, rollback, security, data, or user-facing decision.
- Material concern: should change implementation, tests, evidence, or wording before final delivery.
- Optional improvement: useful but not required for the current goal.
- Invalid objection: contradicts verified evidence or depends on a false premise.
- Residual risk: plausible but not currently verifiable, or not worth further work for the user's goal.

Accept reviewer points only when supported by evidence or strong technical reasoning. Reject points by citing the verified fact they contradict. Gather more evidence before concluding if a material disagreement depends on facts.

## Post-Review Changes

- If Codex changes the implementation, evidence artifact, screenshot ordering, report generation, or final wording after Claude/Kimi review, disclose that change in the final convergence summary.
- Do not imply the reviewer saw a post-review change that was made after the review completed.
- Rerun external review only when the post-review change can alter correctness, safety, mergeability, live behavior, or the core conclusion.
- For low-risk presentational or evidence-packaging fixes, it is acceptable to skip a second external review, but label them as post-review local adjustments.

## Evidence Rules

- Prefer live repo, runtime, browser, CI, logs, database state, or external-system proof over model agreement.
- Do not treat `message sent`, `delivery confirmed`, `agent busy`, and `agent executed with visible output` as equivalent.
- Do not call work done because both models agree. Call it done only when success criteria are met or remaining risk is explicit and acceptable.
- Do not overclaim a validated slice as full completion of the upstream goal.
- Preserve exact repo, worktree, issue, PR/MR, branch, port, command, artifact, and URL identifiers when they matter.

## State Labels

Use these labels for execution tasks:

- Planned: approach exists, no file/runtime change verified.
- Edited: changes made, verification not yet run or not yet passed.
- Locally tested: local tests or scripts passed.
- Browser/runtime verified: user-visible or running-system proof was checked.
- CI verified: remote CI or pipeline passed.
- Externally confirmed: GitHub/GitLab/deploy/customer-facing state was checked.
- Blocked: same blocker remains after reasonable attempts or required input is missing.
- Residual risk accepted: unresolved risk remains, but it is explicit and acceptable for this decision.

## Example

User request: `找 Claude 会诊一下这个 MR 能不能 merge。`

1. Codex inspects the MR, diff, CI, tests, runtime/browser proof, and open review state.
2. Codex writes a first-pass verdict: `Do not merge yet; one stale-row blocker remains after failed refresh.`
3. Codex sends Claude a narrow attack prompt with exact evidence and allowed read-only scope.
4. Claude challenges missing tests, downgrade risks, stale assumptions, or overclaims.
5. Codex accepts or rejects each point based on evidence, gathers more proof if it can change the verdict, and returns a final merge/block decision.

## Final Output Contract

Default to this concise shape unless the user requests another format:

```md
## Final conclusion
Answer plus confidence: high, medium, or low.

## Evidence
- Verified facts and proof.

## External review
Claude model and effort requested, actual model if visible, fallback if any, post-review changes not reviewed, and main objections.

## Convergence
- Accepted: reviewer points adopted and why.
- Rejected: reviewer points rejected and why.
- Still open: residual risks or unknowns.

## Next step
Execute, merge, block, investigate, ask for a specific decision, or report complete.
```

For communication deliverables, convert the converged result into the requested audience's language after the peer-review loop. Use Chinese when the user asks for `中文报告`; use polished English for external GitHub/GitLab reviewer-facing text unless instructed otherwise.
