# Agent Web App Testing

English | [简体中文](README.zh-CN.md)

Playwright Python testing for AI agent web apps: streaming chat, visible progress, human-in-the-loop questions, pause, and resume.

Agent interfaces often fail between submission and final answer: silent waits, stalled streams, broken input prompts, or sessions that never resume. This small wrapper adds those checks to [Anthropic's `webapp-testing`](https://github.com/anthropics/skills/tree/main/skills/webapp-testing).

Use it for ChatGPT-style interfaces, tool-using agents, and workflows that stop for human input.

## What it enforces

- visible text or state progress at least once every 15 seconds
- `running -> streaming -> waiting_user -> running -> completed`
- human-question pause and same-flow resume
- question handling independent of model-generated wording
- non-empty final response

The 15-second rule limits silence, not total runtime. A five-minute task passes when users keep seeing progress. Fifteen silent seconds fails.

## Files

- `SKILL.md` — short operating guide
- `templates/test_agent_flow.py` — runnable flow template with detailed comments

## UI contract

Expose stable selectors from the application:

- Agent root: `data-agent-state`
- prompt: `data-testid="agent-prompt"`
- send control: `data-testid="agent-send"`
- question container: `data-testid="agent-question"`
- answer option: `data-testid="agent-answer-option"`

Keep streamed output, tool status, questions, and visible heartbeat inside the Agent root. Hidden SSE or WebSocket activity does not count as user feedback.

Dynamic question text is expected. The template selects answer controls by semantic attributes, never display text. Add `data-answer-id` when a test must choose a specific answer.

## Use

Copy `SKILL.md` and `templates/` into your skills directory. Update target URL, prompt, and selectors in `templates/test_agent_flow.py`, then run it with an existing Playwright Python setup:

```bash
pytest templates/test_agent_flow.py
```

The template expects Playwright's `page` fixture. Browser setup, traces, screenshots, and standard assertions remain owned by `webapp-testing` or your existing test harness.

## License

MIT. Independent community project; not affiliated with Anthropic.
