---
name: agent-webapp-testing
description: Test AI-featured web apps with Playwright Python, including streaming, stable selector contracts, commit-locked checkpoint fixtures, resume, completion, and recovery.
---

# Agent Web App Testing

Reuse Anthropic [`webapp-testing`](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) for browser interaction, logs, screenshots, and assertions.

Test Agent UI as state machine: `running -> streaming -> waiting_user -> running -> completed`.

Use `templates/test_agent_flow.py`. Fail after 15 seconds without visible text or state change.

Never locate Agent questions or answers by display text. Use stable `data-testid` and `data-answer-id`; text may vary by prompt, language, or model. Read `references/selector-contract.md` when designing or reviewing selectors.

For UI states after slow Agent work, record a checkpoint from the project's real API, Agent, LLM, and database once, then replay that capture in fast UI tests. Never hand-write synthetic SSE events. Read `references/checkpoint-fixtures.md` and adapt `templates/resume_checkpoint.py` for the project's URLs. Store captures only in a gitignored path, lock each capture to the exact full commit SHA, and refuse missing, synthetic, or mismatched fixtures instead of silently running the slow Agent path. Checkpoints must not add controls to the user-facing UI.

Keep one from-scratch live test for the complete Agent integration path. Save trace, screenshots, final response, and HTML QA evidence.
