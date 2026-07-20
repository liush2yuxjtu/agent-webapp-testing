# Agent Web App Testing

English | [简体中文](README.zh-CN.md)

**Go grab a coffee. Let the test handle the rest.**

This small Playwright Python wrapper checks the whole Agent flow from prompt to completion, tests “Agent asks—you answer—Agent continues,” and can save test states tied to the current code version so the next run does not start from scratch. Stable selector contracts handle dynamic wording, while 15 seconds without visible progress becomes an explicit failure.

Built on [Anthropic's `webapp-testing`](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) for streaming chat, tool-using agents, and human-in-the-loop workflows.

## What it does for you

- **Checks the whole journey** — from sending a task to final completion
- **Handles Agent questions** — verifies that answering lets the same flow continue
- **Skips the long wait next time** — resumes from a saved test state

## Why this exists

Normal web tests submit an action and assert the final DOM. Agent interfaces have a longer failure surface:

```text
submit -> running -> streaming -> waiting_user -> resumed -> completed
```

A final-answer assertion misses stalled streams, invisible tool work, broken question dialogs, and sessions that never resume. This template checks progress between those states.

## What it tests

- dynamic model wording through stable semantic selectors
- no visible text or state change for 15 seconds
- stalled streaming without imposing a short total timeout
- `waiting_user` questions and same-flow resume
- local checkpoints locked to the full commit SHA
- explicit Agent errors and non-empty final output

## Installation

This repository is an Agent Skill, not a Python package. Keep `SKILL.md` and `templates/` in the same skill directory. Installing the skill does not require `pip install`.

### Codex

Install for all projects:

```bash
git clone https://github.com/liush2yuxjtu/agent-webapp-testing.git \
  "$HOME/.agents/skills/agent-webapp-testing"
```

For one project, clone it to `.agents/skills/agent-webapp-testing` inside that project. Restart Codex, then prompt:

```text
Use agent-webapp-testing to test this AI Agent UI.
```

See [Using skills in Codex](https://developers.openai.com/codex/skills).

### Claude Code

Copy the whole repository into a supported user-level or project-level Agent Skills location, keeping `SKILL.md` at the skill root. Restart Claude Code, then ask it to use `agent-webapp-testing`. Follow Anthropic's current custom-skill documentation for the location used by your version.

### Claude.ai

Create an upload-ready ZIP with `SKILL.md` at its root:

```bash
git clone https://github.com/liush2yuxjtu/agent-webapp-testing.git
cd agent-webapp-testing
zip -r ../agent-webapp-testing.zip SKILL.md templates references
```

Upload `agent-webapp-testing.zip` through Claude.ai custom Skills, enable it, then ask Claude to use `agent-webapp-testing`.

### Recommended companion skill

This wrapper builds on Anthropic [`webapp-testing`](https://github.com/anthropics/skills/tree/main/skills/webapp-testing). Install both when browser discovery, screenshots, traces, and server management are needed.

### Run the Python template

Playwright dependencies are needed only when running the template:

```bash
python -m pip install pytest pytest-playwright
python -m playwright install chromium
pytest templates/test_agent_flow.py
```

Before running, start the target app and update URL, prompt, and stable selectors in `templates/test_agent_flow.py`.

## UI contract

Expose stable attributes from the application:

- Agent root: `data-agent-state`
- prompt: `data-testid="agent-prompt"`
- send control: `data-testid="agent-send"`
- question container: `data-testid="agent-question"`
- answer option: `data-testid="agent-answer-option"`

Keep streamed output, tool status, questions, and visible heartbeat inside the Agent root. Hidden SSE or WebSocket traffic does not count as user feedback.

Question and answer wording may change by prompt, language, or model. Tests select semantic attributes instead of display text:

```python
agent = page.locator("[data-agent-state]")
question = agent.locator("[data-testid='agent-question']")
question.locator(
    "[data-testid='agent-answer-option'][data-answer-id='approve']"
).click()
```

Do not identify business choices by generated wording, translated text, display-only CSS classes, or `nth(2)`. See [`references/selector-contract.md`](references/selector-contract.md) for the full contract.

## Commit-locked checkpoints

A checkpoint is a developer fixture, not an expert-user feature. It lets most UI tests start directly from a fixed state such as `waiting_user` or `completed`, instead of waiting for the model to repeat earlier work.

```text
.agent/agent-webapp-checkpoints/
└── <full-commit-sha>/
    └── waiting-user/
        ├── manifest.json
        └── response.sse
```

Fixtures live under the Git-ignored `.agent/` directory. Before loading one, compare its `source_commit` with `git rev-parse HEAD` exactly. A missing or mismatched fixture must fail with a regeneration message rather than silently falling back to a slow Agent run.

Use `templates/resume_checkpoint.py` to replay the captured SSE response with Playwright, enter through the normal application URL, and assert `data-agent-state` before interacting. Keep one real UAT that starts from the prompt to verify the full integration path. See [`references/checkpoint-fixtures.md`](references/checkpoint-fixtures.md) for the complete example.

## Silence rule

`MAX_SILENCE = 15` is an inactivity budget, not a total test timeout. Each visible state or text change resets the window. Fifteen seconds without either raises:

```text
AssertionError: No visible Agent progress for 15 seconds
```

## Repository contents

- `SKILL.md` — short operating guide for coding agents
- `templates/test_agent_flow.py` — simple live-flow test template
- `templates/resume_checkpoint.py` — Playwright checkpoint replay helper
- `references/selector-contract.md` — selector design that survives dynamic wording
- `references/checkpoint-fixtures.md` — commit-locked local checkpoint design

## Scope

One guide, two small templates, and two design references—no custom framework. Use the existing Playwright stack for everything it already handles well.

## License

MIT. Independent community project; not affiliated with Anthropic.
