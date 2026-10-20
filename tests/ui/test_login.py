import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage


# Pytest discovers functions named test_*. The arguments request fixtures from
# conftest.py, so each test receives a fresh page and the configured credentials.
def test_successful_login(page: Page, credentials: dict[str, str]):
    # The Page Object handles how to log in; this test still decides what counts
    # as success. Constructing it wraps this test's existing, isolated page.
    login_page = LoginPage(page)
    login_page.login(credentials["username"], credentials["password"])

    # expect retries until the expected state appears or its timeout expires.
    # Verify the destination and visible content, rather than just that we clicked.
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
    expect(page.get_by_text("Products", exact=True)).to_be_visible()
    # A count of zero checks that the Login button is absent from the page.
    expect(login_page.login_button).to_have_count(0)


# Run this function as two separate test cases, changing only one field each time.
# Pytest supplies invalid_field from this list, rather than from a fixture.
@pytest.mark.parametrize("invalid_field", ["username", "password"])
def test_invalid_credentials(
    page: Page, credentials: dict[str, str], invalid_field: str
):
    # Copy before modifying: credentials is shared across the whole test session.
    # Changing the original dictionary would affect later tests.
    login_data = credentials.copy()
    # Keep the other field valid so each case isolates one invalid input.
    login_data[invalid_field] += "_invalid"
    login_page = LoginPage(page)
    login_page.login(login_data["username"], login_data["password"])

    # The correct rejection message proves why login failed.
    expect(login_page.error_message).to_have_text(
        "Epic sadface: Username and password do not match any user in this service",
    )
    expect(login_page.error_message).to_be_visible()
    # Also confirm the user remains on the login screen.
    expect(page).to_have_url("https://www.saucedemo.com/")
    expect(login_page.login_button).to_be_visible()


def test_locked_user(page: Page, credentials: dict[str, str]):
    # This is a public SauceDemo test account. Use the correct demo password
    # to verify account lockout rather than incorrect-password handling.
    login_page = LoginPage(page)
    login_page.login("locked_out_user", credentials["password"])

    expect(login_page.error_message).to_have_text(
        "Epic sadface: Sorry, this user has been locked out."
    )
    expect(login_page.error_message).to_be_visible()
    expect(page).to_have_url("https://www.saucedemo.com/")
    expect(login_page.login_button).to_be_visible()


# Each row becomes an independent test with its own fresh browser context.
# True means leave that field empty. id gives the case a readable output name.
# When both fields are empty, SauceDemo reports the username validation first.
@pytest.mark.parametrize(
    ("empty_username", "empty_password", "expected_error"),
    [
        pytest.param(True, False, "Username is required", id="empty-username"),
        pytest.param(False, True, "Password is required", id="empty-password"),
        pytest.param(True, True, "Username is required", id="both-empty"),
    ],
)
def test_required_fields(
    page: Page,
    credentials: dict[str, str],
    empty_username: bool,
    empty_password: bool,
    expected_error: str,
):
    # Conditional expressions select an empty string or the valid fixture value
    # according to this case's parameters.
    username = "" if empty_username else credentials["username"]
    password = "" if empty_password else credentials["password"]
    login_page = LoginPage(page)
    login_page.login(username, password)

    # The f-string inserts this case's expected validation message.
    expect(login_page.error_message).to_have_text(f"Epic sadface: {expected_error}")
    expect(login_page.error_message).to_be_visible()
    expect(page).to_have_url("https://www.saucedemo.com/")
    expect(login_page.login_button).to_be_visible()
