# Commit-locked Agent checkpoints

Use checkpoints to start UI tests after slow Agent work without replaying the model. They are developer fixtures, never user-facing controls.

## Contract

- Capture only from a committed revision.
- Store under `.agent/agent-webapp-checkpoints/<full-commit-sha>/<checkpoint>/`; `.agent/` is gitignored.
- Record `checkpoint`, `source_commit`, and `expected_state` in `manifest.json`.
- Create a fresh thread/session for every resumed test.
- Compare the manifest SHA with `git rev-parse HEAD` before loading.
- Fail fast when the fixture is absent or mismatched. Do not silently run the slow Agent flow.
- Keep one separate from-scratch live test for the full integration path.

```json
{
  "checkpoint": "waiting_user",
  "source_commit": "a1b2c3d4e5f67890...",
  "expected_state": "waiting_user"
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
    return fixture
```

After the app restores the fixture, navigate through its normal URL and assert the root `data-agent-state` equals `expected_state` before interacting. Treat these untracked fixtures as disposable local caches; CI must create or obtain its own matching fixture.
