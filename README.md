# Agent Web App Testing

English | [简体中文](README.zh-CN.md)

**Survive dynamic wording. Turn every silent stall into an explicit failure.**

An agent can stop producing output without failing or finishing. This small Playwright Python wrapper catches that state after 15 seconds without visible progress. It also keeps model-generated wording out of selectors.

Built on [Anthropic's `webapp-testing`](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) for streaming chat, tool-using agents, and human-in-the-loop workflows.

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
- explicit Agent errors and non-empty final output

## Install in Codex

```bash
git clone https://github.com/liush2yuxjtu/agent-webapp-testing.git \
  "$HOME/.agents/skills/agent-webapp-testing"
```

For one repository, clone it to `.agents/skills/agent-webapp-testing` inside that repository. Restart Codex, then ask it to use `agent-webapp-testing`. See [Using skills in Codex](https://developers.openai.com/codex/skills).

## Install in Claude

- **Claude.ai:** Download this repository as a ZIP, upload it through the custom-skill uploader, then enable it.
- **Claude Code:** Copy the whole repository into a supported user or project Agent Skills location, keeping `SKILL.md` at the skill root, then restart Claude Code.

Ask Claude to use `agent-webapp-testing` by name. Follow Anthropic's official custom-skill guide for the current product and version.

## Quick start

From the installed or extracted skill directory:

```bash
python -m pip install pytest pytest-playwright
playwright install chromium
```

Then:

1. Start the web app under test.
2. Update URL, prompt, and selectors in `templates/test_agent_flow.py`.
3. Run:

```bash
pytest templates/test_agent_flow.py
```

The script is a template, so selector adaptation is required. Browser lifecycle, traces, screenshots, and server management stay with `webapp-testing` or the existing Playwright harness.

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
question = page.locator("[data-testid='agent-question']")
question.locator("[data-testid='agent-answer-option']").first.click()
```

Add `data-answer-id` when a test must choose a specific business answer.

## Silence rule

`MAX_SILENCE = 15` is an inactivity budget, not a total test timeout. Each visible state or text change resets the window. Fifteen seconds without either raises:

```text
AssertionError: No visible Agent progress for 15 seconds
```

## Repository contents

- `SKILL.md` — short operating guide for coding agents
- `templates/test_agent_flow.py` — simple test template with detailed comments

## Scope

One guide, one template, no custom framework. Use the existing Playwright stack for everything it already handles well.

## License

MIT. Independent community project; not affiliated with Anthropic.
