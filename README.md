# QA Nexus

A Quality Engineering portfolio project, built progressively to connect automated
tests, useful diagnostics, and eventually a results dashboard.

## Current milestone

Ten SauceDemo UI scenarios using Python, Pytest, and Playwright:

- Successful login and navigation to Products
- Invalid username and invalid password
- Locked user
- Empty username, empty password, and both fields empty
- Add a product to the cart, checking its name, price, badge count, and quantity
- Remove a product from the cart and verify the empty cart and product button state
- Logout and reject direct product-page access afterward in the same browser context

The original `test_example.py` remains the initial Python.org smoke test.

## Run the authentication tests

Use the existing `.venv`. The current environment has Pytest 9.1.1,
Playwright 1.63.0, pytest-html 4.2.0, and Chromium installed.
Direct Python dependencies are recorded in `requirements.txt`. On a fresh
environment, install them with `python -m pip install -r requirements.txt`, then
install the browser with `python -m playwright install chromium`. No future
backend, API, or frontend packages are included yet.

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

## Run the cart workflows

After setting the same environment variables, watch both cart tests:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ui/test_cart.py -v --headed --slowmo 500
```

Expected result: **2 passed**. Each test logs in and adds its own product.
The addition test checks the Sauce Labs Backpack costs $29.99 and verifies one
matching cart item. The removal test removes its item, verifies the cart rows and
badge disappear, then returns to Products and checks Add to cart is available again.
The browser closes automatically; no purchase is made.

Run only the removal test to confirm it works independently:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ui/test_cart.py::test_remove_product_from_cart -v --headed --slowmo 500
```

Run authentication and cart tests together:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ui -v
```

Expected result: **10 passed**, or **11 passed** with `python -m pytest -v`,
which includes the original Python.org smoke test.

## Watch logout

After setting the same credentials, run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ui/test_logout.py -v --headed --slowmo 500
```

Expected result: **1 passed**. The test logs in, opens the menu, logs out, then
attempts to reopen Products in the same context. It checks the redirect and
access-denied message. This covers browser route protection, not server-side
session or token revocation.

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

## HTML test report

`pytest-html` creates a browser-readable summary of the run. It is the only direct
dependency introduced for this milestone; pip also installs its required template
and metadata packages. After setting the same credentials, run the full suite:

```powershell
.\.venv\Scripts\python.exe -m pytest -v --html=reports/report.html --self-contained-html
```

Expected result: **11 passed** and a generated `reports/report.html` file. Open it
from PowerShell with:

```powershell
Start-Process .\reports\report.html
```

The report shows the run summary, environment metadata, individual test outcomes,
durations, and captured failure output. Use the result checkboxes to filter tests;
expand a result row to inspect details. The six rejected-login scenarios still
show Passed because the expected validation was displayed.

`--html` selects the output path. `--self-contained-html` embeds the report's
normal assets in the HTML file, so no separate CSS folder is needed. The standard
reporting mode follows the plugin's [official usage guide](https://pytest-html.readthedocs.io/en/latest/user_guide.html#creating-a-self-contained-report).
Screenshots and traces remain separate diagnostic files; this increment does not
embed them in the report. They are created only on failure, whereas the HTML
report is created for passing runs too.

The command overwrites `reports/report.html` each time. For a different run,
choose a different filename with `--html`. All generated reports remain ignored
by Git. Report generation is opt-in: omit both flags for the usual terminal run.
To watch the UI and generate a report together, run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ui -v --headed --slowmo 500 --html=reports/ui-report.html --self-contained-html
```

That command includes only the **10 SauceDemo UI tests**.

## Failure diagnostics

Tests using the UI `page` fixture now record Playwright traces automatically.
When a test body or a dependent setup fixture fails, cleanup saves:

```text
reports/<run-id>/<test-name-and-id>/
    screenshot.png
    trace.zip
```

The terminal prints the diagnostics directory in captured teardown output.
Open `screenshot.png` to see the page at failure. Open a trace locally with:

```powershell
.\.venv\Scripts\python.exe -m playwright show-trace "reports\<run-id>\<test-name-and-id>\trace.zip"
```

Replace the example path with the actual generated path. Trace Viewer lets you
inspect recorded browser actions, DOM snapshots, screenshots, and network activity.
It records browser activity, not every Python assertion; use the Pytest traceback
alongside the trace to understand the failure.

Passing tests discard their traces and do not create diagnostic directories. Run IDs
and test IDs prevent different failures from overwriting each other. Diagnostic
files may include submitted form data and network details; `reports/` is excluded
from Git and is not pushed to GitHub.

Capture is best effort if a page or browser has crashed: a screenshot may be
unavailable, and capture errors are printed without replacing the test error.
Failures before a page exists cannot have page screenshots. Errors in cleanup
after artifact capture are outside this increment's coverage. The standalone
Python.org smoke test does not use these fixtures and has no automatic diagnostics.

These files are debugging artifacts alongside the HTML test-result report.
A temporary intentional-failure probe validated capture and was removed;
the normal suite still contains eleven tests.

## How the tests work

`tests/ui/conftest.py` provides fixtures that Pytest discovers automatically.
Tests request a fixture by naming it as a function argument.

- `credentials` reads environment variables once per session and reports missing
  configuration explicitly.
- `browser` launches Chromium once per session, headless unless `--headed` is set.
- `page` creates a fresh browser context for each test, opens the login page, and
  closes the context afterward, including when a test fails. Contexts isolate
  cookies and browser storage while sharing the browser process.
- `authenticated_page` requests `page` and `credentials`, logs in, verifies Products
  is ready, and returns the page. It runs once per test, so cart and logout tests
  reuse setup instructions while still receiving independent login sessions.
  Cleanup stays with the underlying `page` fixture.
- `pytest_runtest_makereport` remembers each test's setup/body results in Pytest's
  stash. The page fixture reads them before closing the context to decide whether
  to save evidence. Recording starts before navigation to include login setup.

`tests/ui/test_login.py` keeps actions and assertions visible in the tests.
Parameterization runs the same behavior with different inputs as separate test
cases. Invalid-input tests copy credential data before changing it so shared
fixture data remains unchanged.

Cart and logout tests request `authenticated_page` because login is their setup.
Authentication tests continue to request `page` and perform login themselves
because login is the behavior under test. No fixture is marked `autouse`: tests
explicitly opt into the starting state they need.

Locators use placeholders and button roles. Playwright's `expect` assertions
retry until the expected state appears or their timeout expires; there are no
fixed sleeps. Rejected logins check both the error message and that the user
remains on the login page.

The cart tests demonstrate state transition testing: an empty cart becomes a cart
containing one specific product, and removing the item makes it empty again.
Each test establishes its own starting state. The tests scope actions to a product's card, use
SauceDemo's `data-test` attributes where accessible roles are insufficient, and
check fixed expected values rather than deriving expectations from the UI.

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
- Why verify an item exists before testing its removal?
- How does Arrange, Act, Assert make a state transition test easier to understand?
- How can fixtures depend on other fixtures without sharing login state across tests?
- Why test a protected page after logout in the same browser context?
- What can a trace show that a screenshot cannot?
- Why capture diagnostics before closing the browser context?
- How does a test-result report differ from screenshots and traces?
- Why is an application validation error sometimes a passing test result?

## Roadmap

Page Objects where useful, API testing,
result persistence, FastAPI, a React dashboard, and GitHub Actions.
