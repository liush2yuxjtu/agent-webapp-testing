# Agent Web App Testing

English | [简体中文](README.zh-CN.md)

**Fail AI agent UAT when users see no progress for 15 seconds.**

Small Playwright Python wrapper for streaming chat, tool-using agents, and human-in-the-loop workflows. It adds agent state checks to [Anthropic's `webapp-testing`](https://github.com/anthropics/skills/tree/main/skills/webapp-testing).

A five-minute task can pass. A 15-second silent screen cannot.

## Why this exists

Normal web tests submit an action and assert the final DOM. Agent interfaces have a longer failure surface:

```text
submit -> running -> streaming -> waiting_user -> resumed -> completed
```

A final-answer assertion misses stalled streams, invisible tool work, broken question dialogs, and sessions that never resume. This template checks progress between those states.

## What it tests

- visible text or state changes at least once every 15 seconds
- streaming progress without imposing a short total timeout
- `waiting_user` questions and same-flow resume
- dynamic question text through stable semantic selectors
- explicit Agent errors and non-empty final output

## Quick start

```bash
git clone https://github.com/liush2yuxjtu/agent-webapp-testing.git
cd agent-webapp-testing
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
