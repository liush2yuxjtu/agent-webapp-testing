import os
import time

from playwright.sync_api import Locator, Page

MAX_SILENCE = 15


def snapshot(agent: Locator) -> tuple[str, str]:
    # Keep all visible progress under Agent root: streamed output, tool status,
    # questions, and heartbeat. Hidden network traffic is not user feedback.
    return agent.get_attribute("data-agent-state") or "", agent.inner_text()


def wait_change(page: Page, agent: Locator, previous: tuple[str, str]):
    # This limits silence, not total runtime. Every visible change resets window.
    deadline = time.monotonic() + MAX_SILENCE
    while time.monotonic() < deadline:
        current = snapshot(agent)
        if current[0] == "error":
            raise AssertionError(current[1][-300:])
        if current != previous:
            return current
        page.wait_for_timeout(250)
    raise AssertionError("No visible Agent progress for 15 seconds")


def test_agent_pause_resume(page: Page):
    page.goto(os.environ.get("AGENT_WEBAPP_URL", "http://localhost:3000"))
    agent = page.locator("[data-agent-state]").first
    current = snapshot(agent)

    # Stable selectors keep prompt and button wording independent from test.
    page.locator("[data-testid='agent-prompt']").fill("Run task requiring clarification")
    page.locator("[data-testid='agent-send']").click()

    while current[0] != "waiting_user":
        current = wait_change(page, agent, current)

    # Question and answer text may vary by prompt, language, or model.
    question = page.locator("[data-testid='agent-question']")
    question.locator("[data-testid='agent-answer-option']").first.click()

    # Resume same flow. Long work passes while visible progress changes every 15s.
    while current[0] != "completed":
        current = wait_change(page, agent, current)

    assert current[1].strip(), "Completed Agent must show final response"
