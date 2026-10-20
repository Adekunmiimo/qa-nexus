# QA Nexus: concepts, terms, and how the project works

This is your study guide to the code currently in QA Nexus. Read it alongside
the files rather than trying to memorise everything at once. Each major section
explains a concept, why it matters, and where it appears in our project.

The project currently has **10 SauceDemo UI test cases and 1 Python.org smoke
test**. It has a Login Page Object, reusable fixtures, failure screenshots and
traces, and HTML reporting. A backend, database, React dashboard, API tests, and
GitHub Actions pipeline are **planned, not implemented**.

## Reading map

1. [What we are building](#1-what-we-are-building)
2. [Files and responsibilities](#2-files-and-responsibilities)
3. [Python concepts used in the code](#3-python-concepts-used-in-the-code)
4. [Environment and dependencies](#4-environment-and-dependencies)
5. [Testing concepts and terminology](#5-testing-concepts-and-terminology)
6. [Pytest and fixtures](#6-pytest-and-fixtures)
7. [Playwright and browser automation](#7-playwright-and-browser-automation)
8. [Page Object Model](#8-page-object-model)
9. [Diagnostics and reporting](#9-diagnostics-and-reporting)
10. [A complete test run explained](#10-a-complete-test-run-explained)
11. [Commands and terminal results](#11-commands-and-terminal-results)
12. [Git and GitHub](#12-git-and-github)
13. [Future concepts](#13-future-concepts-not-built-yet)
14. [Study plan and self-check](#14-study-plan-and-self-check)

## 1. What we are building

**Quality Assurance (QA)** means activities that help prevent quality problems
through better processes and practices. **Software testing** evaluates software
and provides evidence about its behavior and risks. **Quality Engineering (QE)**
applies engineering practices throughout development to improve quality and
testability. These ideas overlap; testing alone cannot guarantee defect-free software.

**Test automation** uses code to perform checks repeatedly. In QA Nexus, Python
tests use Playwright to interact with public websites and verify results.

**SDET** means Software Development Engineer in Test: a role combining software
development skills with test design, automation, and quality engineering.

Our **application under test (AUT)** is currently SauceDemo. It is the shopping
application being checked. **QA Nexus** is our testing project and future quality
platform. SauceDemo's storefront is not a frontend we built ourselves.

Our tools have different jobs:

| Tool | Definition | Its current job |
| --- | --- | --- |
| Python | Programming language | Express setup, actions, data, and checks |
| Pytest | Test framework and runner | Discover cases, provide fixtures, execute tests, report outcomes |
| Playwright | Browser automation library | Control Chromium and inspect UI state |
| pytest-html | Pytest reporting plugin | Generate a readable HTML result report |
| PowerShell | Command shell | Set environment variables and run commands |
| VS Code | Code editor | Read and edit the project and use its terminal |
| Git | Version control system | Record local changes as commits |
| GitHub | Repository hosting and collaboration service | Store the pushed repository online |

## 2. Files and responsibilities

**Architecture** means how a system's parts are organised and how they work
together. We introduce structure when it solves a real problem.

| File or folder | Responsibility |
| --- | --- |
| [test_example.py](../test_example.py) | Original Python.org title check; starts its own browser |
| [tests/ui/test_login.py](../tests/ui/test_login.py) | Seven authentication cases |
| [tests/ui/test_cart.py](../tests/ui/test_cart.py) | Independent addition and removal workflows |
| [tests/ui/test_logout.py](../tests/ui/test_logout.py) | Logout and product-route protection |
| [tests/ui/conftest.py](../tests/ui/conftest.py) | Shared fixtures, CLI options, and diagnostic hooks |
| [pages/login_page.py](../pages/login_page.py) | Login locators and reusable login action |
| [pages/__init__.py](../pages/__init__.py) | Marks pages as a regular Python package |
| [requirements.txt](../requirements.txt) | Current direct Python dependencies and versions |
| [.gitignore](../.gitignore) | Files and directories Git should ignore when untracked |
| reports/ | Local generated HTML reports, screenshots, and traces |
| [README.md](../README.md) | Project overview and operating instructions |
| [interview-preparation.md](interview-preparation.md) | Sample interview answers with explanations |
| [session-summary.md](session-summary.md) | Milestones, verification results, and resume notes |

**Separation of responsibilities** means each part has a clear job: fixtures
prepare resources, Page Objects describe interactions, and tests verify behavior.

**Maintainability** means being able to understand and change code safely.
Centralising login locators improves maintainability because one UI change does
not require searching through every test for duplicated selectors.

## 3. Python concepts used in the code

### Modules, imports, functions, and arguments

A **module** is an importable unit of Python code, commonly a `.py` file.
A **package** groups modules under an import name. Our `pages` directory contains
`__init__.py`, making it a regular package.

```python
from pages.login_page import LoginPage
```

This imports the class from our own project. `from playwright.sync_api import
Page` imports a type from an installed external library.

A **function** is a named block of reusable behavior declared with `def`.
A **parameter** is a name in its definition; an **argument** is a value supplied
when calling it. In `login(username, password)`, username and password are
parameters; the particular credential strings passed at runtime are arguments.

A **return value** is the result handed back by a function. `return page` supplies
an existing page to the caller. A function without an explicit returned value
returns `None`, Python's value representing no result or absence.

### Variables and collections

| Term | Definition | Project example |
| --- | --- | --- |
| Variable | A name referring to a value or object | `product_name` refers to the backpack name |
| String, str | Text | `"Sauce Labs Backpack"` |
| Integer, int | Whole number | `500` milliseconds for slow motion |
| Boolean, bool | True or False | `empty_username` selects whether to leave a field empty |
| Dictionary, dict | Mapping of keys to values | credentials maps username and password keys to strings |
| List | Ordered collection | the invalid-field parameter values |
| Tuple | Ordered collection whose entries cannot be reassigned | environment-variable names in credentials setup |
| Attribute | Value or method accessed through an object | `login_page.login_button` |
| Method | Function associated with an object or class | `login_page.login(...)` |

**Mutation** changes an existing object. Our session-scoped credentials dictionary
is shared, so changing it could affect later tests. `credentials.copy()` makes a
new dictionary before we add `_invalid` to a value. A shallow copy is enough for
our string values; nested mutable objects would need additional thought.

A **comprehension** builds a collection concisely. This means “collect required
names whose environment values are missing or empty”:

```python
missing = [name for name in variable_names if not os.environ.get(name)]
```

An **f-string** inserts values into text: `f"Epic sadface: {expected_error}"`.
A **conditional expression** chooses one of two values:
`"" if empty_username else credentials["username"]`.

### Classes, objects, self, and __init__

A **class** defines a kind of object. An **instance** is a particular object
created from that class. `LoginPage(page)` creates an instance wrapping a tab.

```python
login_page = LoginPage(page)
login_page.login(username, password)
```

`__init__` initialises the new instance. `self` refers to that instance, allowing
its methods to use attributes such as `self.username_input`. `self` is a naming
convention for the instance parameter; it does not refer to the whole project.

Constructing LoginPage stores locators. It does **not** launch Chromium or log in.
Calling `.login(...)` performs the form actions.

### Type hints

**Type hints** describe expected inputs and outputs. They help readers and tools;
they do not generally enforce those types automatically at runtime.

| Annotation | Meaning here |
| --- | --- |
| `page: Page` | The value should be a Playwright Page object |
| `dict[str, str]` | Dictionary with string keys and values |
| `-> None` | The function has no meaningful returned result |
| `-> Page` | The function returns a Page |
| `Iterator[Page]` | Our generator fixture yields Page values |
| `Generator[None, pytest.TestReport, pytest.TestReport]` | The hook wrapper yields no value, receives a report, then returns a report |

A type hint does not create a browser or make a fixture run. Pytest supplies
fixtures based on their argument names, not their annotations.

### Decorators, generators, and context managers

A **decorator** attaches behavior or metadata to a function using `@...`.
`@pytest.fixture` registers a fixture; `@pytest.mark.parametrize` creates input
variations; `@pytest.hookimpl` identifies a hook implementation.

A function containing **yield** is a **generator function**. Execution can pause
at yield and later resume. In our fixtures, code before yield sets up a resource,
yield supplies it, and code afterward handles cleanup.

```python
context = browser.new_context()
try:
    yield context.new_page()
finally:
    context.close()
```

This is a shortened teaching example. The real fixture also navigates, records
tracing, checks reports, and saves diagnostics.

A **context manager**, used through `with`, manages entry and exit from a block.
`with sync_playwright() as playwright:` starts Playwright and stops it when the
block exits. This does not remove our responsibility to close browser resources.

### Exceptions and cleanup

An **exception** signals an error or unusual condition. `raise` creates or
propagates an exception. `try` encloses work, `except` handles a matching error,
and `finally` runs cleanup whether the protected work succeeds or raises.

`Error` in our imports is Playwright's error class. `OSError` represents operating
system errors, such as inability to write a file. Diagnostic capture catches
these so an unavailable screenshot does not replace the original test error.

A **traceback** shows the Python calls and locations involved in an exception.
It is different from a Playwright trace archive.

### Standard-library helpers in conftest.py

The **standard library** is functionality included with Python, unlike external
packages that we install using pip.

| Helper | Purpose in our code |
| --- | --- |
| `os.environ` | Read the current process's environment variables |
| `argparse.ArgumentTypeError` | Explain an invalid CLI delay value |
| `re.sub` | Replace unsafe filename characters using a regular expression |
| `Path` from pathlib | Build paths, make directories, and locate report files |
| `datetime.now()` | Timestamp the diagnostic run identifier |
| `uuid4()` | Generate a random identifier to distinguish runs |
| `sha256(...)` | Derive a short suffix from a test's full ID to distinguish filenames |
| `any(...)` | Check whether at least one recorded report failed |

A **regular expression** is a text-matching pattern. Our pattern replaces
characters outside a permitted set before constructing a Windows-friendly name.
A **hash** is a derived representation of input. Here SHA-256 helps name files;
it is not being used as password storage or authentication.

## 4. Environment and dependencies

An **interpreter** executes Python code. A **virtual environment** is a project
environment with its own Python executable and installed packages. `.venv` keeps
QA Nexus dependencies separate from other Python projects.

When PowerShell displays `(.venv)`, activation has adjusted command lookup so
`python` normally resolves to the virtual environment. You can also use
`.\.venv\Scripts\python.exe` directly without activating it.

A **dependency** is a package our project needs. A **direct dependency** is one
we deliberately list; a **transitive dependency** is needed by one of those
packages. pytest-html, for example, requires supporting template/metadata packages.

**pip** installs Python distributions. `requirements.txt` lists our current direct
dependencies. A **version pin**, such as `pytest-html==4.2.0`, selects that exact
version. Our manifest pins direct dependencies; it is not a complete lock file
pinning every transitive dependency and browser binary.

**Chromium** is the browser engine/browser Playwright currently launches. Its
binary is separate from the Python Playwright package. Installing the library
alone does not necessarily install the browser.

An **environment variable** is a named value made available to a process.
We set SauceDemo credentials in PowerShell, and Python reads the inherited values.
They last for that terminal session and need setting again in a new terminal.

A **secret** is sensitive information such as a real password or API token.
**Configuration** is information that can vary outside code, including credentials
and launch options. Our demo credentials are supplied through environment variables.
Do not copy real credentials into source files or public documentation.

An **.env file** is a common local convention for configuration. Ignoring it with
Git does not load it into Python. We have no dotenv loader installed: `os.environ`
reads process values, not `.env` automatically.

## 5. Testing concepts and terminology

| Concept | Definition | QA Nexus example or status |
| --- | --- | --- |
| Test scenario | Behavior or situation to investigate | User submits invalid credentials |
| Test case | A concrete check with starting conditions, inputs, actions, and expected results | Invalid password produces the specified error and no access |
| Test suite | Related collection of test cases | Our SauceDemo UI cases |
| Test run | One execution of selected cases | A command that executes all eleven cases |
| Test data | Inputs used by a test | Credentials, product name, expected price |
| Precondition | State required before exercising the behavior | Logged in with an item in the cart before removal |
| Expected result | What should happen according to the requirement | Cart is empty after its last item is removed |
| Actual result | What the application did | Observed cart rows, badge, and button state |
| Assertion | Code comparing actual behavior with an expectation | `expect(badge).to_have_text("1")` |
| Positive testing | Check supported behavior with valid inputs | Successful login |
| Negative testing | Check handling of invalid input or denied actions | Invalid credentials and locked user |
| Validation testing | Check required fields and input rules | Empty username/password messages |
| Boundary testing | Check limits and nearby values | Future case: a documented input-length limit; not implemented yet |
| Authentication | Establishing who a user is | Login using credentials |
| Authorization | Deciding what a user may access | Product-route rejection after logout; limited UI coverage |
| State transition | Change from one application state to another | Empty cart -> one item -> empty again |
| Regression testing | Rechecking existing behavior after a change | Running the suite after introducing LoginPage |
| Smoke testing | Small set of basic checks indicating whether deeper testing is worthwhile | The original Python.org page/title check |
| Retesting | Rechecking a specific defect after a fix | Rerunning logout after correcting its role locator |
| UI testing | Test through visible user-interface controls | Typing into the login form and clicking buttons |
| End-to-end testing | Check a complete workflow across the relevant system boundaries | Our tests cover browser workflows; no purchase or owned backend integration is tested |
| Cross-browser testing | Check behavior in multiple browser engines | Planned; only Chromium is currently used |
| Test coverage | The behaviors, risks, code, or platforms exercised | Current scenarios cover selected login/cart/logout behavior, not all SauceDemo features |

An **oracle** is the basis for deciding the expected result. The cart test uses
explicit expected product information rather than copying the displayed price
and comparing the page with itself. Real projects need expectations grounded in
approved requirements or controlled data.

**Arrange, Act, Assert** organises a test into preparing conditions, performing
the behavior, and verifying the outcome. The removal test arranges an item in the
cart, removes it, then checks rows, badge, and product-button state.

**Test isolation** means preventing one test's state from affecting another.
Our fresh contexts isolate browser storage. They do not automatically isolate
shared backend accounts or databases in applications that store data server-side.

A **flaky test** inconsistently passes and fails without a relevant intended
change. Timing, shared state, unstable locators, and external network issues are
possible causes. Diagnose the evidence rather than automatically blaming the app.

A **false positive** here means a check appears to pass without proving the
required behavior. An empty cart alone is weak evidence of removal if no item was
ever added. A **false alarm** is a reported failure caused by a test or environment
problem rather than a product defect. State your terminology clearly in interviews.

An **application validation error** can be the correct expected result. Our six
negative login cases pass when SauceDemo rejects them correctly. Only one of the
seven authentication cases should reach Products.

**100% progress** in Pytest means all selected cases completed, not that every
case passed or that the application has 100% coverage. Read the final summary.

## 6. Pytest and fixtures

### Discovery, collection, and parameterization

**Discovery** finds candidate tests using naming rules. In our project, files
named `test_*.py` and functions named `test_*` are discovered. **Collection** builds
the test items Pytest will execute.

**Parameterization** gives one function multiple input sets, each collected as a
separate case. Our four login functions produce seven cases:

| Function | Collected cases |
| --- | ---: |
| test_successful_login | 1 |
| test_invalid_credentials | 2: invalid username and invalid password |
| test_locked_user | 1 |
| test_required_fields | 3: username empty, password empty, both empty |

`pytest.param(..., id="both-empty")` gives a case a readable **parameter ID**.
A **node ID** identifies a collected test, such as
`tests/ui/test_login.py::test_required_fields[both-empty]`.
It can be used to select that specific case.

### Fixtures and dependency injection

A **fixture** supplies setup, resources, or data. A test requests it by argument
name. **Dependency injection** means supplying dependencies from outside instead
of requiring the test to construct everything internally.

```python
def test_add_product_to_cart(authenticated_page: Page):
    page = authenticated_page
```

Pytest resolves the named fixture. The assignment creates a convenient local
name referring to the same Page, not a copy of the browser tab.

**conftest.py** is a special Pytest configuration/fixture module automatically
discovered for its directory and descendants. Tests do not manually import its
fixtures or execute that file as a script. Built-in fixtures come from Pytest;
custom fixtures are ones we define.

### Fixture scope and resource ownership

**Scope** determines how long a fixture instance is reused. Pytest supports
function, class, module, package, and session scopes. We currently use function
and session scopes.

| Fixture | Scope | Responsibility |
| --- | --- | --- |
| credentials | session | Read configured strings once per test session |
| artifact_root | session | Choose the diagnostic directory for this run |
| browser | session | Launch Chromium once and close it at session cleanup |
| page | function, the default | Create an isolated context/tab, record tracing, clean up |
| authenticated_page | function | Use that fresh page to log in and verify Products |

Our fixture dependency chain for cart/logout tests is:

```text
browser -> page -> authenticated_page -> test
             ^            ^
       artifact_root   credentials
```

This shows dependencies, not a guaranteed order for independent sibling fixtures.
**Setup** prepares a dependency; **teardown** releases it. Dependent fixtures finish
before their underlying resources are torn down.

The fixture that creates a resource should generally own its cleanup.
authenticated_page returns an existing Page, so it needs no extra yield cleanup.
The underlying page fixture still closes the context after the dependent test.

### Pytest hooks and reports

A **hook** is an extension point that Pytest calls at a particular stage.
A **plugin** packages extensions to the framework. conftest can implement hooks;
pytest-html is an installed plugin that adds report generation.

| Item | Meaning in this project |
| --- | --- |
| pytest_addoption | Hook registering our custom --headed and --slowmo options |
| pytestconfig | Built-in fixture exposing configuration and CLI option values |
| request | Built-in fixture giving access to the current fixture/test context |
| request.node | Current test item |
| pytest_runtest_makereport | Hook producing a report for a test phase |
| TestReport | Pytest object with phase and outcome information |
| setup, call, teardown | Resource preparation, test body, resource cleanup phases |
| stash | Typed-key storage attached to a Pytest object |
| StashKey | Distinguishes our stored data from other plugins' data |

Our **hook wrapper** uses `report = yield` to let the underlying report operation
run, receives its result, stores it, and returns it unchanged. Its yield serves
the hook protocol; it is not a fixture providing a page.

The page fixture reads setup/body reports during cleanup. A test-body assertion
failure is recorded by Pytest; it is not normally thrown into the fixture's yield
as though the test body were inside the fixture's try block. That is why we use
reports to decide whether to save diagnostics. A failure in the page fixture's
own setup is caught directly before its setup report exists.

**pytest.fail(...)** explicitly signals failure. If it occurs during fixture
setup, the case is reported as an ERROR because the test body could not run.
`pytrace=False` hides an unnecessary Python traceback for missing configuration.

## 7. Playwright and browser automation

### Browser, context, and page

| Term | Meaning |
| --- | --- |
| Browser | Launched browser process, currently Chromium |
| BrowserContext | Isolated browser session with its own cookies and storage |
| Page | Tab or popup within a context |
| Cookie | Small piece of browser-associated website data often used in sessions |
| Browser storage | Client-side data such as localStorage and sessionStorage |
| Session state | Information allowing the application to treat a user as logged in or retain other state |
| URL | Address of a web resource, such as the inventory page |
| Navigation | Loading or moving to another page/route |

`browser.new_context()` creates the isolated session; `context.new_page()` opens
its tab; `page.goto(...)` navigates. The `sync_api` exposes synchronous calls that
read sequentially in our tests. Other API styles exist, but we have not introduced
asynchronous Python test code.

**Headless** execution has no visible window. **Headed** execution shows the
window. `--headed` changes the launch setting; it does not change expected results.
**Slow motion** adds a delay to browser operations for observation. It is not a
solution for synchronisation problems.

### DOM, elements, roles, and locators

The **DOM**, Document Object Model, is the browser's structured representation of
the page. An **element** is a node such as an input, button, or link. An HTML
**attribute** supplies information such as placeholder, href, role, or data-test.

A **locator** describes how to find an element. It is not a screenshot coordinate
or a permanently stored copy of a DOM element. Playwright resolves locators for
operations, so our product locator can find the current product after navigation.

| Locator feature | Definition | Example |
| --- | --- | --- |
| Placeholder | Hint text in a form input | get_by_placeholder("Username", exact=True) |
| Role | Accessible UI purpose, such as button | get_by_role("button", name="Login", exact=True) |
| Accessible name | Name assistive technology uses for a control | Login or Open Menu |
| Text locator | Locate by displayed text | get_by_text("Products", exact=True) |
| CSS selector | Pattern for selecting DOM elements | `[data-test="inventory-item"]` |
| Test attribute | Attribute provided to support reliable test targeting | SauceDemo's data-test |
| Scoped locator | Search within an already selected container | product.get_by_role(...) |
| filter(has=...) | Select containers containing a matching descendant | The card containing the exact backpack name |
| exact=True | Require an exact name/text match for the locator option | Avoid matching a longer, different product name |

**Accessibility** makes software usable with assistive technology and supports
semantic controls. Role locators use the accessibility model, not only HTML tags.
SauceDemo's Logout is an `<a>` with `role="button"`, so we locate it as a button.

A **stable locator** is based on meaningful, dependable information. Styling
classes, layout positions, or long DOM paths can change without a behavior change.
We prefer semantic locators and use data-test for controls/containers without a
useful accessible name. XPath is another query language; we do not currently use it.

### Actions, waiting, and assertions

`fill(value)` replaces an input's contents. `click()` performs a click.
**Auto-waiting** means Playwright waits for relevant conditions before supported
actions, such as an element being visible, enabled, and able to receive the click.
This does not automatically know every business-specific readiness condition.

**Retrying assertions** such as `expect(...).to_have_text(...)` wait for the
expected state until their timeout. A **timeout** is the permitted waiting limit;
it is not necessarily time the operation always takes.

| Assertion | What it proves |
| --- | --- |
| to_have_url(...) | Current page has the expected URL |
| to_be_visible() | Matching element is visible |
| to_have_text(...) | Matching element has the expected text |
| to_have_count(1) | Exactly one element matches |
| to_have_count(0) | No elements match, rather than merely being hidden |

The original `assert "Python" in page.title()` is a plain Python assertion.
It evaluates the value once; it does not retry like a Playwright expect assertion.
We do not add `time.sleep()` to guess when a UI update will be complete.

## 8. Page Object Model

**Page Object Model (POM)** organises page locators and reusable interactions in
objects. It is a design approach, not an additional package we installed.

Our **LoginPage** stores four locators and provides one action:

```python
login_page = LoginPage(page)
login_page.login(credentials["username"], credentials["password"])
expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
```

The first line initialises the wrapper, the second interacts with the form, and
the third checks this scenario's result. Invalid-input cases use the same action
but expect rejection. The login action does not require a successful outcome.

**Abstraction** presents a meaningful operation while hiding its internal steps.
**Encapsulation** groups related data and behavior. Our class groups locators and
form interaction; Python attributes here remain publicly accessible to tests.
**Refactoring** changes code structure while preserving intended behavior. We
verified the POM refactor with the existing eleven tests rather than adding new
cases solely to mirror the class implementation.

| Fixture | Page Object |
| --- | --- |
| Provides setup, data, or resources | Groups page-specific locators and actions |
| Pytest controls its scope and lifetime | A Python object constructed wherever needed |
| Our page fixture owns context cleanup | LoginPage does not own browser cleanup |
| authenticated_page requires successful setup | login supports both accepted and rejected inputs |

More classes do not automatically mean better architecture. Avoid a giant page
class, a complicated inheritance hierarchy, or action names that hide the test's
purpose. We have not created a CartPage just to match a folder diagram.

## 9. Diagnostics and reporting

**Diagnostics** are evidence used to investigate failures. An **artifact** is a
generated file from a test run. A **report** summarises execution results.

| Artifact | Purpose | When we save it |
| --- | --- | --- |
| screenshot.png | Full-page image near the failure | Failed UI test/setup, when page is available |
| trace.zip | Recorded browser actions, snapshots, screenshots, and network information | Failed UI test/setup, best effort |
| report.html | Run results, durations, metadata, and captured failure output | When HTML reporting flags are supplied, even if tests pass |

A **snapshot** in a trace captures a representation of the page for inspection.
The **Trace Viewer** opens a trace archive locally. A trace is not simply a video
and does not record every Python assertion; use it with the terminal traceback.

**Metadata** is descriptive information, such as Python version, platform, and
loaded plugin versions. **Duration** measures elapsed execution time. **Captured
output** is printed/logged text Pytest collects and can include with test results.
We currently print diagnostic messages; we have not built a structured application
logging system.

The diagnostics sequence is:

```text
Start context tracing -> navigate -> execute setup/test
    -> read phase reports before context cleanup
        -> failure: try screenshot and save trace.zip
        -> success: discard trace
    -> close context
```

Artifact paths include a timestamp/random run ID, a sanitised test name, and a
hash suffix derived from the node ID. This reduces naming collisions and prevents
one run's evidence from overwriting another's.

**Best effort** means we try to collect evidence without promising every artifact
can always be produced. Closed pages cannot provide screenshots. Failures before
a page exists and cleanup errors after capture are outside current screenshot
coverage. The standalone Python.org test does not use this diagnostics fixture.

The HTML report is **self-contained** when its normal JavaScript/CSS assets are
embedded in the HTML. Our screenshots and traces remain separate; we have not
attached them to the report. The default report filename is overwritten by the
next run using that filename.

Generated artifacts can contain entered data or network information, so reports/
is Git-ignored. This does not automatically delete those files or make them safe
to publish. The source code and documentation are pushed; generated evidence stays local.

## 10. A complete test run explained

For `test_add_product_to_cart`, the flow is:

1. Pytest collects the test and sees its authenticated_page argument.
2. It resolves that fixture's dependencies: credentials and a fresh page.
3. The session-scoped browser launches if it does not already exist.
4. The page fixture creates a context, starts tracing, and opens SauceDemo.
5. authenticated_page constructs LoginPage and submits the configured credentials.
6. The fixture verifies Products is ready and returns the Page.
7. The test verifies the backpack's identity and price, adds it, checks the badge,
   opens the cart, and verifies its row, price, and quantity.
8. Pytest creates the test-body report. Our hook stores its outcome.
9. The page fixture uses that report to retain or discard diagnostics, then closes
   the context. The browser process can serve the next test's fresh context.
10. At the end of the session the browser is closed. If requested, pytest-html
    writes the HTML report, and Pytest prints the final run summary.

No other test must log in or add a product first. The test requests the starting
state it needs and creates its own product state through the UI.

## 11. Commands and terminal results

Commands below assume the activated project environment and current directory.
In a new terminal, configure credentials first:

```powershell
$env:SAUCEDEMO_USERNAME = 'standard_user'
$env:SAUCEDEMO_PASSWORD = '<public demo password displayed on SauceDemo>'
```

Replace the placeholder with the public password displayed on the demo site.

```powershell
# Seven authentication cases
python -m pytest tests/ui/test_login.py -v

# Watch the two cart cases
python -m pytest tests/ui/test_cart.py -v --headed --slowmo 500

# Collect without running browser tests
python -m pytest --collect-only -q

# Full eleven-test suite and HTML report
python -m pytest -v --html=reports/report.html --self-contained-html

# Open the generated report
Start-Process .\reports\report.html

# Open a failed test's trace; replace the placeholder path
python -m playwright show-trace "reports\<run>\<test>\trace.zip"
```

| Command part | Meaning |
| --- | --- |
| python -m pytest | Execute the pytest module using this Python interpreter |
| -v | Verbose test names/results |
| -q | Quieter output |
| --collect-only | Discover/collect cases without executing them |
| --headed | Our custom option for a visible browser in UI fixtures |
| --slowmo 500 | Our custom option delaying browser operations by 500 ms |
| --tb=short | Shorter Python traceback formatting |
| --html=... | pytest-html output path |
| --self-contained-html | Embed the HTML report's normal assets |
| Start-Process | PowerShell command opening a file through its associated application |

The custom browser options apply to UI tests using our fixtures, not to the
original standalone test's manually launched browser.

| Result | Meaning |
| --- | --- |
| PASSED | The executed test met its assertions |
| FAILED | The test body raised a failure, assertion, or other unhandled exception |
| ERROR | Setup or teardown failed; inspect which phase failed |
| SKIPPED | The case was deliberately not executed due to a skip condition |
| XFAIL / XPASS | Expected failure / unexpectedly passing expected-failure case; not currently used |

An **exit code** is the status a program returns to its caller. Pytest normally
returns 0 when the run succeeds; failed tests, usage errors, and no-tests-collected
conditions have other codes. CI can use the code to decide whether a job passes.

**Debugging** means identifying the cause of unexpected behavior from evidence.
First read the failing test and phase, then the message/traceback, then screenshots
and traces. Reproduce the affected case independently before rewriting working code.

## 12. Git and GitHub

| Term | Definition and project use |
| --- | --- |
| Repository, repo | Project files plus Git's version history |
| Working tree | Files currently checked out on your computer |
| Diff | Difference between file versions |
| Staging area | Selected changes prepared for the next commit |
| Commit | Recorded snapshot of selected changes, with a message and identifier |
| Commit hash | Identifier such as the abbreviated ID shown in git log |
| Branch | Movable name pointing to a line of development; currently main |
| Remote | Named reference to another repository location |
| origin | Conventional name for our GitHub remote |
| Push | Send local commits to a remote branch |
| Fetch | Download remote history/references without integrating them into your branch |
| Pull | Fetch and integrate remote changes according to Git settings/options |
| Pull request, PR | Proposed change for review on a hosting service such as GitHub |
| Merge | Integrate lines of development |
| .gitignore | Patterns for untracked files Git should not automatically add |

Our GitHub repository is https://github.com/Adekunmiimo/qa-nexus. A local Windows
directory is not a GitHub URL. Committing saves locally; pushing publishes commits
to the configured remote. They are separate operations.

`.venv`, caches, `.env`, debug.log, and reports/ are ignored. An ignore rule does
not remove a file already tracked or erase secrets from past commits. Our current
milestones have been pushed to main. The planned feature-branch/PR workflow is
not yet evidence of an established review process for this project.

## 13. Future concepts: not built yet

These definitions explain the roadmap. Do not describe them as completed features
when presenting QA Nexus. Do not install their dependencies just to study the terms.

| Term | Definition | Intended future use |
| --- | --- | --- |
| API | Defined interface for software components to communicate | Test services and exchange test-result data |
| HTTP | Web request/response protocol | Send API requests and interpret responses |
| REST | Architectural style using resources and standard web semantics | Design QA Nexus resource APIs |
| HTTP methods | Operations such as GET, POST, PUT, PATCH, DELETE | Read, create, replace, update, or delete appropriate resources |
| Status code | Numeric response outcome, such as 200, 201, 400, 401, or 404 | Assert API behavior |
| JSON | Structured text format with objects, arrays, and values | Request/response data |
| Schema | Definition of expected data shape and constraints | Validate API payloads and stored models |
| Backend | Service-side application logic and data handling | Receive and retrieve real test runs |
| FastAPI | Python web framework for APIs | Proposed backend framework |
| Pydantic | Python data validation/model library | Validate backend input and output |
| Database | Organised persistent data storage | Save projects, cases, runs, and results |
| Persistence | Data surviving beyond the current process | Keep test history after a run ends |
| SQLite | Embedded relational database | Initial local storage |
| SQL | Language for querying/manipulating relational data | Work with stored results |
| ORM | Object-relational mapping between code objects and database tables | Proposed SQLAlchemy models |
| Migration | Versioned database-schema change | Evolve tables when needed |
| Frontend | User-facing application interface | A QA Nexus dashboard we build, separate from SauceDemo |
| React | UI library based on components | Dashboard interface |
| TypeScript | JavaScript with a static type system | Typed frontend code |
| Vite | Frontend development/build tool | Run and build the frontend |
| Tailwind CSS | Utility-class-based CSS framework | Style dashboard components |
| Analytics | Calculations and visualisations that help interpret data | Trends, pass rates, recent failures |
| CI | Continuous integration: automated checks as changes are integrated | Run tests on pushes/PRs |
| CD | Continuous delivery or deployment, depending on the workflow | Prepare releases or deploy when explicitly configured |
| GitHub Actions | Workflow automation service | Future CI test jobs and artifact upload |
| YAML | Structured configuration format | Define future workflow steps |
| Parallel execution | Run multiple tasks at the same time | Potential future speed improvements with careful isolation |
| Code coverage | Measurement of which application code executes under tests | Useful later for code we own; different from scenario coverage |
| Logging | Recorded runtime events with useful context | More structured diagnostics as the platform grows |
| Mock | Controlled replacement for a dependency in a test | Possible future isolated tests; current UI tests use the real demo site |
| AI quality engineering | Evaluation of AI-system behavior, risks, and reliability | Longer-term direction; no AI service is integrated now |

## 14. Study plan and self-check

You do not need to master the hooks before understanding your first login test.

1. **Start with the behavior.** Read test_example.py and test_successful_login.
   Explain the action and the expected result in ordinary words.
2. **Understand the browser.** Describe browser versus context versus page. Watch
   one test with headed mode and connect the visible actions to the code.
3. **Understand shared setup.** Read credentials, browser, page, then
   authenticated_page. Explain their scope and who closes each resource.
4. **Understand test design.** Read negative login cases and both cart tests.
   Explain why rejected login is correct and why removal needs its own setup.
5. **Understand the Page Object.** Read LoginPage, then its callers. Distinguish
   the reusable interaction from the expected outcome.
6. **Understand evidence.** Open the HTML report and an existing diagnostic trace.
   Explain what each can and cannot tell you.
7. **Study the advanced support code.** Work through CLI registration, phase
   reports, stash, path naming, and artifact capture after the simpler concepts.
8. **Practise speaking.** Use the interview guide to answer in your own words
   and point to an actual project example for each answer.

Before moving on, try explaining these without reading the answer:

- Why are seven authentication cases produced from four functions?
- Why should only one of those cases reach Products?
- Why can two cart tests run in either order?
- What is the difference between page and authenticated_page?
- Why does LoginPage.login not assert a successful login?
- Why are there no new screenshots after a completely passing run?
- What does 100% in the terminal actually tell you?
- What does a Git commit do that a push does not, and vice versa?
- Which QA Nexus features exist today, and which are only planned?

If you can connect each answer to the code, you are building understanding rather
than memorising tool names. Use [the interview guide](interview-preparation.md)
for sample answers and [the README](../README.md) for run commands.
