"""Minimal Playwright helper for resuming a UI test from a recorded SSE checkpoint."""

import json
import subprocess
from pathlib import Path
from uuid import uuid4

from playwright.sync_api import Locator, Page, expect


CHECKPOINTS = Path(".agent/agent-webapp-checkpoints")


def load_checkpoint(name: str) -> tuple[dict, str]:
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True
    ).strip()
    directory = CHECKPOINTS / commit / name
    manifest = json.loads((directory / "manifest.json").read_text())
    assert manifest["source_commit"] == commit, "Stale checkpoint; regenerate it"
    assert manifest["recorded_from"] == "real_api", "Synthetic checkpoint rejected"
    return manifest, (directory / "response.sse").read_text()


def resume_from_checkpoint(
    page: Page,
    *,
    name: str,
    api_url_glob: str,
    resume_url: str,
    fresh_thread_id: str | None = None,
) -> Locator:
    """Replay a real SSE capture into a fresh thread and verify restored UI state."""
    manifest, response = load_checkpoint(name)
    thread_id = fresh_thread_id or str(uuid4())
    response = response.replace(manifest["source_thread_id"], thread_id)

    page.route(
        api_url_glob,
        lambda route: route.fulfill(
            status=200,
            content_type="text/event-stream",
            headers={"cache-control": "no-cache"},
            body=response,
        ),
    )
    page.goto(resume_url.format(thread_id=thread_id))

    agent = page.locator("[data-agent-state]").first
    expect(agent).to_have_attribute("data-agent-state", manifest["expected_state"])
    return agent
