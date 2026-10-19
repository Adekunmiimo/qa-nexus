# QA Nexus

A Quality Engineering portfolio project, built progressively to connect automated
tests, useful diagnostics, and eventually a results dashboard.

## Current milestone

Eight SauceDemo UI scenarios using Python, Pytest, and Playwright:

- Successful login and navigation to Products
- Invalid username and invalid password
- Locked user
- Empty username, empty password, and both fields empty
- Add a product to the cart, checking its name, price, badge count, and quantity

The original `test_example.py` remains the initial Python.org smoke test.

## Run the authentication tests

Use the existing `.venv`; this milestone requires no additional dependencies.
The current environment has Pytest 9.1.1, Playwright 1.63.0, and Chromium installed.

Open https://www.saucedemo.com/ and use the public `standard_user` account and
password displayed on its login page. In PowerShell, set them for this terminal:

```powershell
$env:SAUCEDEMO_USERNAME = 'standard_user'
$env:SAUCEDEMO_PASSWORD = '<public demo password displayed on SauceDemo>'
.\.venv\Scripts\python.exe -m pytest tests/ui/test_login.py -v
```

Replace the password placeholder before running. These environment variables last
for the terminal session; no `.env` loader is installed. Use only the public demo
credentials, and keep real secrets out of source control.

Expected result: **7 passed**, with internet access to SauceDemo required.
To run the original smoke test too:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

## Run the cart workflow

After setting the same environment variables, watch the new test:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ui/test_cart.py -v --headed --slowmo 500
```

Expected result: **1 passed**. It logs in independently, checks the Sauce Labs
Backpack costs $29.99, adds it, and verifies one matching item in the cart.
The browser closes automatically; no purchase is made.

Run authentication and cart tests together:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ui -v
```

Expected result: **8 passed**, or **9 passed** with `python -m pytest -v`,
which includes the original Python.org smoke test.

## Watch the browser

After setting the environment variables above, run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ui/test_login.py -v --headed --slowmo 500
```

`--headed` opens a visible Chromium window. `--slowmo 500` adds a 500 ms delay to
Playwright operations so you can follow the actions. It is optional and accepts
non-negative whole numbers. The browser closes automatically when the run ends.

To watch only the successful login:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ui/test_login.py::test_successful_login -v --headed --slowmo 500
```

Omit both options for normal headless execution without added delays. These are
custom options for the UI browser fixture; the original `test_example.py` launches
its own browser and does not use them. Slow motion helps observation; assertions
still use Playwright's waiting behavior to check the result.

## How the tests work

`tests/ui/conftest.py` provides fixtures that Pytest discovers automatically.
Tests request a fixture by naming it as a function argument.

- `credentials` reads environment variables once per session and reports missing
  configuration explicitly.
- `browser` launches Chromium once per session, headless unless `--headed` is set.
- `page` creates a fresh browser context for each test, opens the login page, and
  closes the context afterward, including when a test fails. Contexts isolate
  cookies and browser storage while sharing the browser process.

`tests/ui/test_login.py` keeps actions and assertions visible in the tests.
Parameterization runs the same behavior with different inputs as separate test
cases. Invalid-input tests copy credential data before changing it so shared
fixture data remains unchanged.

Locators use placeholders and button roles. Playwright's `expect` assertions
retry until the expected state appears or their timeout expires; there are no
fixed sleeps. Rejected logins check both the error message and that the user
remains on the login page.

The cart test demonstrates state transition testing: an empty cart becomes a cart
containing one specific product. It scopes actions to the product's card, uses
SauceDemo's `data-test` attributes where accessible roles are insufficient, and
checks fixed expected values rather than deriving expectations from the UI.

Page Object Model will be introduced when reuse across workflows justifies it.
This suite depends on a public external site, so network outages and site changes
can cause failures that need diagnosis.

## Interview practice

- What is a fixture, and how does `yield` support teardown?
- Why share a browser but create a new context for each test?
- How does parameterization differ from a loop inside one test?
- Why use Playwright's `expect` for changing UI state?
- Why copy session-scoped test data before modifying it?
- Why is checking the cart badge insufficient to prove the correct item was added?
- Why should expected product prices be independent of the displayed value?

## Roadmap

Cart removal and additional product workflows, Page Objects where useful, API testing, failure
diagnostics, result persistence, FastAPI, a React dashboard, and GitHub Actions.
