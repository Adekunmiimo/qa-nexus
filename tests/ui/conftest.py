import argparse
import os
import re
from collections.abc import Generator, Iterator
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

import pytest
from playwright.sync_api import Browser, Error, Page, expect, sync_playwright

from pages.login_page import LoginPage


# Pytest's stash stores data on a test item without inventing custom attributes.
TEST_REPORTS = pytest.StashKey[dict[str, pytest.TestReport]]()


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item,
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    # A test has setup, call (the test body), and teardown reports. Let Pytest
    # produce the report first, then remember it for our page fixture's cleanup.
    report = yield
    item.stash.setdefault(TEST_REPORTS, {})[report.when] = report
    return report


@pytest.fixture(scope="session")
def artifact_root(pytestconfig: pytest.Config) -> Path:
    # Separate runs so failures never overwrite evidence from an earlier run.
    # No directory is created unless a test actually fails.
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid4().hex[:8]
    return pytestconfig.rootpath / "reports" / run_id


def save_failure_artifacts(page: Page, directory: Path) -> None:
    # Save independently: a crashed/closed page may prevent a screenshot, while
    # a trace might still be available. Diagnostics must not hide the test error.
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        print(f"Could not create diagnostics directory: {error}")
        return
    print(f"Failure diagnostics: {directory}")
    try:
        page.screenshot(path=directory / "screenshot.png", full_page=True, timeout=5000)
    except (Error, OSError) as error:
        print(f"Could not save screenshot: {error}")
    try:
        page.context.tracing.stop(path=directory / "trace.zip")
    except (Error, OSError) as error:
        print(f"Could not save trace: {error}")


def non_negative_integer(value: str) -> int:
    # Reject invalid delays at command parsing, before opening a browser.
    delay = int(value)
    if delay < 0:
        raise argparse.ArgumentTypeError("delay must be zero or greater")
    return delay


def pytest_addoption(parser: pytest.Parser) -> None:
    # This Pytest hook registers our CLI options; pytest-playwright is not needed.
    group = parser.getgroup("QA Nexus browser options")
    group.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Show the browser window for tests using the UI browser fixture.",
    )
    group.addoption(
        "--slowmo",
        type=non_negative_integer,
        default=0,
        metavar="MILLISECONDS",
        help="Delay Playwright operations for observation (default: 0).",
    )


# Pytest discovers fixtures in conftest.py automatically for tests in this folder
# and its subfolders. Tests request them by using their names as arguments.
# Type hints describe the values supplied; they do not create those values.
# Session scope means this fixture runs once and its result is reused in this run.
@pytest.fixture(scope="session")
def credentials() -> dict[str, str]:
    # Read the variables set with $env:... in PowerShell, keeping the password
    # outside source code. os.environ does not automatically read .env files.
    variable_names = ("SAUCEDEMO_USERNAME", "SAUCEDEMO_PASSWORD")
    missing = [name for name in variable_names if not os.environ.get(name)]
    if missing:
        # Stop setup with a useful message instead of attempting login with
        # missing data. pytrace=False hides an unnecessary Python traceback.
        pytest.fail(
            f"Set these environment variables before running: {', '.join(missing)}. "
            "See README.md for instructions.",
            pytrace=False,
        )
    return {
        "username": os.environ["SAUCEDEMO_USERNAME"],
        "password": os.environ["SAUCEDEMO_PASSWORD"],
    }


@pytest.fixture(scope="session")
def browser(pytestconfig: pytest.Config) -> Iterator[Browser]:
    # pytestconfig is a built-in fixture that gives access to CLI option values.
    # The context manager starts Playwright and stops it when this block exits.
    with sync_playwright() as playwright:
        # --headed makes headless False, opening a visible browser window.
        # slow_mo is a viewing aid, not a replacement for Playwright's waiting.
        browser = playwright.chromium.launch(
            headless=not pytestconfig.getoption("--headed"),
            slow_mo=pytestconfig.getoption("--slowmo"),
        )
        # yield supplies the browser to dependent fixtures, then pauses here.
        # After those fixtures finish, Pytest resumes here for cleanup.
        # Iterator[Browser] describes a generator that yields a Browser object.
        yield browser
        browser.close()


# Without an explicit scope, a fixture runs once per test case (function scope).
@pytest.fixture
def page(
    browser: Browser, request: pytest.FixtureRequest, artifact_root: Path
) -> Iterator[Page]:
    # Pytest supplies the browser fixture above. Each new context has separate
    # cookies and browser storage, preventing login state from leaking between tests.
    context = browser.new_context()
    page = None
    setup_failed = False
    try:
        # Recording must start before navigation to capture setup as well as the
        # test actions. Successful tests discard the recording during cleanup.
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        # A page is a browser tab. Every test starts at the same login screen.
        page = context.new_page()
        page.goto("https://www.saucedemo.com/")
        yield page
    except Exception:
        # If this fixture fails before yield, its setup report is not ready yet.
        setup_failed = True
        raise
    finally:
        reports = request.node.stash.get(TEST_REPORTS, {})
        failed = setup_failed or any(report.failed for report in reports.values())
        try:
            if failed and page is not None:
                # Parameter IDs can contain characters Windows forbids in paths.
                # A hash distinguishes tests with the same name in different files.
                name = re.sub(r"[^a-zA-Z0-9_-]", "_", request.node.name)[:80]
                suffix = sha256(request.node.nodeid.encode()).hexdigest()[:8]
                save_failure_artifacts(page, artifact_root / f"{name}-{suffix}")
            elif page is not None:
                context.tracing.stop()
        finally:
            # Capture evidence before closing; teardown still runs on failure.
            context.close()


@pytest.fixture
def authenticated_page(page: Page, credentials: dict[str, str]) -> Page:
    # Fixtures can request other fixtures. Pytest builds this chain for each test:
    # browser -> page (fresh context) -> authenticated_page (login on that page).
    # This reuses login instructions, not a logged-in session between tests.
    # Reuse the action while this fixture owns the successful-login precondition.
    LoginPage(page).login(credentials["username"], credentials["password"])
    # Verify the setup worked before handing the page to a cart or logout test.
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
    expect(page.get_by_text("Products", exact=True)).to_be_visible()
    # No new resource was created here, so return is sufficient. The underlying
    # page fixture still owns cleanup, including if login or a later test fails.
    return page
