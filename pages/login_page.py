from playwright.sync_api import Page


class LoginPage:
    """Keep login locators and actions together; tests decide expected outcomes."""

    def __init__(self, page: Page) -> None:
        # self refers to this LoginPage instance. It wraps an existing tab:
        # creating the object does not open a browser, navigate, or log in.
        self.username_input = page.get_by_placeholder("Username", exact=True)
        self.password_input = page.get_by_placeholder("Password", exact=True)
        self.login_button = page.get_by_role("button", name="Login", exact=True)
        # The validation message has no useful accessible role. SauceDemo's
        # dedicated test attribute is a stable alternative to a styling class.
        self.error_message = page.locator('[data-test="error"]')

    def login(self, username: str, password: str) -> None:
        # Locators describe elements; fill/click perform the actual interactions.
        # This action supports valid, invalid, and empty inputs equally. It must
        # not assume success, because rejection is the goal of negative tests.
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
