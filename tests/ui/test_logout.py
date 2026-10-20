from playwright.sync_api import Page, expect

from pages.login_page import LoginPage


def test_logout_blocks_product_access(authenticated_page: Page):
    # Start logged in through the function-scoped fixture. Other authentication
    # tests still use page directly because login is the behavior they exercise.
    page = authenticated_page
    page.get_by_role("button", name="Open Menu", exact=True).click()
    # SauceDemo assigns role="button" to this <a> element; role locators follow
    # its accessible role, which can differ from the HTML tag's default role.
    page.get_by_role("button", name="Logout", exact=True).click()

    # Verify the visible result of logout, not just that the menu link was clicked.
    expect(page).to_have_url("https://www.saucedemo.com/")
    login_page = LoginPage(page)
    expect(login_page.username_input).to_be_visible()
    expect(login_page.password_input).to_be_visible()
    expect(login_page.login_button).to_be_visible()

    # A redirect alone does not prove access was removed. Attempt to reopen the
    # protected screen in the SAME context, with no fresh context to mask a bug.
    page.goto("https://www.saucedemo.com/inventory.html")
    expect(page).to_have_url("https://www.saucedemo.com/")
    expect(page.get_by_text(
        "Epic sadface: You can only access '/inventory.html' when you are logged in.",
        exact=True,
    )).to_be_visible()
    expect(page.get_by_text("Products", exact=True)).to_have_count(0)
    # This checks the demo's browser-facing route protection. It does not test
    # server-side token revocation, which would need separate API coverage.
