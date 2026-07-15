# Agent Web App Testing

Small wrapper skill and Playwright Python template for AI-featured web apps.

It extends [Anthropic webapp-testing](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) with Agent state-machine checks:

- streaming and visible progress
- 15-second maximum silent period
- human-question pause and resume
- text-independent question selectors
- terminal completion

## Use

Copy `SKILL.md` and `templates/` into your skills directory. Adapt URL, prompt, and stable `data-testid` selectors in `templates/test_agent_flow.py`.

Required UI contract:

- Agent root: `data-agent-state`
- prompt: `data-testid="agent-prompt"`
- send control: `data-testid="agent-send"`
- question: `data-testid="agent-question"`
- answer: `data-testid="agent-answer-option"`

Run with an existing Playwright Python setup:

```bash
pytest templates/test_agent_flow.py
```

Independent community project; not affiliated with Anthropic.
