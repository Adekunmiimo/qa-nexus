import argparse
import os
from collections.abc import Iterator

import pytest
from playwright.sync_api import Browser, Page, sync_playwright


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
def page(browser: Browser) -> Iterator[Page]:
    # Pytest supplies the browser fixture above. Each new context has separate
    # cookies and browser storage, preventing login state from leaking between tests.
    context = browser.new_context()
    try:
        # A page is a browser tab. Every test starts at the same login screen.
        page = context.new_page()
        page.goto("https://www.saucedemo.com/")
        yield page
    finally:
        # finally closes the context and its tabs even if navigation or a test
        # fails. The shared browser stays available for the next test case.
        context.close()
