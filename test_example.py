from playwright.sync_api import sync_playwright


def test_open_python_page():
    # Start Playwright for this test; the context manager stops it on exit.
    with sync_playwright() as p:
        # Launch headless Chromium and open a tab (no visible browser window).
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://www.python.org")

        # This basic Python assertion checks that the title contains "Python".
        # Unlike Playwright's expect assertions, it does not retry the check.
        assert "Python" in page.title()

        # Release the browser resources after a successful assertion. Our newer
        # SauceDemo fixtures also guarantee cleanup when a test fails.
        browser.close()
