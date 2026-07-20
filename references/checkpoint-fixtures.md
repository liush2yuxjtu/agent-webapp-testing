# Commit-locked Agent checkpoints

Use checkpoints to start UI tests after slow Agent work without replaying the model. They are developer fixtures, never user-facing controls.

## Provenance

Record fixtures by running the project's real API path once: real Agent, real LLM, real database, and real SSE response. A fast E2E may intercept the API and replay that recording afterward, but it must never use events hand-authored by a coding agent. Put `"recorded_from": "real_api"`, the source thread ID, and capture timestamp in the manifest, and reject any fixture without that provenance.

## Contract

- Capture only from a committed revision through the real project API.
- Never hand-write or repair SSE event arrays; regenerate them from the API.
- Store under `.agent/agent-webapp-checkpoints/<full-commit-sha>/<checkpoint>/`; `.agent/` is gitignored.
- Record `checkpoint`, `source_commit`, and `expected_state` in `manifest.json`.
- Create a fresh thread/session for every resumed test.
- Compare the manifest SHA with `git rev-parse HEAD` before loading.
- Fail fast when the fixture is absent or mismatched. Do not silently run the slow Agent flow.
- Keep one separate from-scratch live test for the full integration path.

A minimal single-stream fixture contains:

```text
.agent/agent-webapp-checkpoints/<full-commit-sha>/<checkpoint>/
├── manifest.json
└── response.sse   # exact raw response captured from the real API
```

```json
{
  "checkpoint": "waiting_user",
  "source_commit": "a1b2c3d4e5f67890...",
  "expected_state": "waiting_user",
  "recorded_from": "real_api",
  "source_thread_id": "<real-thread-uuid>",
  "recorded_at": "2026-07-20T00:00:00.000Z"
}
```

## Minimal loader

```python
import json
import subprocess
from pathlib import Path


def load_checkpoint(name: str) -> dict:
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True
    ).strip()
    path = Path(".agent/agent-webapp-checkpoints") / commit / name / "manifest.json"
    assert path.exists(), f"Checkpoint missing for {commit}; regenerate it"
    fixture = json.loads(path.read_text())
    assert fixture["source_commit"] == commit, "Stale checkpoint; regenerate it"
    assert fixture["recorded_from"] == "real_api", "Synthetic checkpoint rejected"
    return fixture
```

## Resume with Playwright

Copy or import `templates/resume_checkpoint.py`, then call its helper from a fast test:

```python
from resume_checkpoint import resume_from_checkpoint


def test_resume_at_question(page):
    agent = resume_from_checkpoint(
        page,
        name="waiting_user",
        api_url_glob="**/api/threads/*/events",
        resume_url="http://localhost:3000/threads/{thread_id}",
    )
    agent.locator(
        "[data-testid='agent-answer-option'][data-answer-id='approve']"
    ).click()
```

Adapt only the API glob and normal thread URL to the project. The helper verifies provenance and the current commit, creates a fresh thread ID, replaces the recorded source thread ID in the raw SSE response, installs `page.route(...)`, opens the normal URL, and checks `data-agent-state` against `expected_state` before the test interacts.

If the application requires a server-created thread, create it through the normal API first and pass its ID as `fresh_thread_id`. If reaching the checkpoint requires more than one response, keep the same manifest rules but route each exact recorded response separately; do not combine or invent events.

Treat these untracked fixtures as disposable local caches; CI must create or obtain its own matching real-API recording.
