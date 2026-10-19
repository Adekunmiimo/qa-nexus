import pytest
from playwright.sync_api import Page, expect


# Pytest discovers functions named test_*. The arguments request fixtures from
# conftest.py, so each test receives a fresh page and the configured credentials.
def test_successful_login(page: Page, credentials: dict[str, str]):
    # Match the input's placeholder and the button's accessible role/name.
    # exact=True prevents partial matches; fill() replaces the input's value.
    page.get_by_placeholder("Username", exact=True).fill(credentials["username"])
    page.get_by_placeholder("Password", exact=True).fill(credentials["password"])
    page.get_by_role("button", name="Login", exact=True).click()

    # expect retries until the expected state appears or its timeout expires.
    # Verify the destination and visible content, rather than just that we clicked.
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
    expect(page.get_by_text("Products", exact=True)).to_be_visible()
    # A count of zero checks that the Login button is absent from the page.
    expect(page.get_by_role("button", name="Login", exact=True)).to_have_count(0)


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
    page.get_by_placeholder("Username", exact=True).fill(login_data["username"])
    page.get_by_placeholder("Password", exact=True).fill(login_data["password"])
    page.get_by_role("button", name="Login", exact=True).click()

    # The correct rejection message proves why login failed.
    expect(page.get_by_text(
        "Epic sadface: Username and password do not match any user in this service",
        exact=True,
    )).to_be_visible()
    # Also confirm the user remains on the login screen.
    expect(page).to_have_url("https://www.saucedemo.com/")
    expect(page.get_by_role("button", name="Login", exact=True)).to_be_visible()


def test_locked_user(page: Page, credentials: dict[str, str]):
    # This is a public SauceDemo test account. Use the correct demo password
    # to verify account lockout rather than incorrect-password handling.
    page.get_by_placeholder("Username", exact=True).fill("locked_out_user")
    page.get_by_placeholder("Password", exact=True).fill(credentials["password"])
    page.get_by_role("button", name="Login", exact=True).click()

    expect(page.get_by_text(
        "Epic sadface: Sorry, this user has been locked out.", exact=True
    )).to_be_visible()
    expect(page).to_have_url("https://www.saucedemo.com/")
    expect(page.get_by_role("button", name="Login", exact=True)).to_be_visible()


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
    page.get_by_placeholder("Username", exact=True).fill(username)
    page.get_by_placeholder("Password", exact=True).fill(password)
    page.get_by_role("button", name="Login", exact=True).click()

    # The f-string inserts this case's expected validation message.
    expect(page.get_by_text(f"Epic sadface: {expected_error}", exact=True)).to_be_visible()
    expect(page).to_have_url("https://www.saucedemo.com/")
    expect(page.get_by_role("button", name="Login", exact=True)).to_be_visible()
