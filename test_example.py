from playwright.sync_api import sync_playwright


def test_open_python_page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://www.python.org")

        assert "Python" in page.title()

        browser.close()