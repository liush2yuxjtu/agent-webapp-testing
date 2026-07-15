---
name: agent-webapp-testing
description: Test AI-featured web apps with Playwright Python, including streaming, waiting, variable questions, resume, completion, and recovery.
---

# Agent Web App Testing

Reuse Anthropic [`webapp-testing`](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) for browser interaction, logs, screenshots, and assertions.

Test Agent UI as state machine: `running -> streaming -> waiting_user -> running -> completed`.

Use `templates/test_agent_flow.py`. Fail after 15 seconds without visible text or state change.

Never locate Agent questions or answers by display text. Use stable `data-testid` and `data-answer-id`; text may vary by prompt, language, or model.

Save trace, screenshots, final response, and HTML QA evidence.
