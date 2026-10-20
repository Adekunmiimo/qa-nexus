# QA Nexus interview preparation

These are sample answers to practise in your own words. They describe what we
have implemented; they do not imply that every planned platform feature exists.

For definitions, Python syntax, fixture execution flow, and a study plan, read
the [project concepts guide](project-concepts-guide.md) alongside these answers.

## What problem does Page Object Model solve?

**Sample answer:** Page Object Model groups a page's locators and reusable actions
in one class. It reduces duplicated UI instructions and gives locator changes one
place to be maintained. Tests continue to express scenarios and expected results.

**Explanation and example:** `pages/login_page.py` stores Username, Password,
Login, and the error-message locator. `login(username, password)` fills and submits
the form. Authentication tests and `authenticated_page` reuse that action.
If the Username locator changes, these callers do not each need editing.

## When can Page Object Model become unnecessary complexity?

**Sample answer:** It becomes excessive when abstractions add more work than they
save, giant classes combine unrelated pages, or methods hide the test's purpose.
I introduce small Page Objects when repeated interactions justify them.

**Explanation and example:** QA Nexus started with direct Playwright calls. We
added only LoginPage after the same login actions appeared in tests and setup.
We have no base-page hierarchy or Page Objects for every screen. Cart workflows
remain readable test code until further reuse warrants a separate abstraction.

## Why keep assertions outside the login action?

**Sample answer:** The same interaction can have different expected outcomes.
Keeping scenario assertions in tests lets positive and negative cases reuse the
action without assuming every login should succeed.

**Explanation and example:** A valid login should reach Products; an invalid
password should show an error. Both call `LoginPage.login`. The authenticated
fixture separately checks Products because successful login is its precondition.
This is our project's separation of responsibilities, rather than a universal
rule that no Page Object may ever contain a check.

## What is a fixture, and how does yield support teardown?

**Sample answer:** A fixture provides reusable setup or resources requested by a
test. With a yield fixture, code before yield prepares the resource, yield supplies
it, and code afterward cleans it up when its dependents finish.

**Explanation and example:** The `page` fixture opens a context and tab. Its
finally block closes them even after a test fails. `authenticated_page` creates
no extra resource, so it returns the page and leaves cleanup to `page`.

## Why share a browser but create a new context for each test?

**Sample answer:** Launching a browser is relatively expensive. Sharing the process
reduces startup overhead, while fresh contexts isolate cookies and browser storage.

**Explanation and example:** Our browser fixture has session scope; page has
function scope. Each cart test logs in separately and starts with its own cart.
Context isolation does not automatically isolate shared server-side database data.

## How does parameterization differ from a loop inside a test?

**Sample answer:** Parameterization creates a separate collected test case for each
input set, with individual setup, results, and selection. A loop remains one test;
an ordinary assertion failure stops the loop and hides later checks.

**Explanation and example:** The three empty-field rows become three named test
cases, each receiving a fresh page, rather than three steps sharing one page.

## Why use Playwright's expect for changing UI state?

**Sample answer:** Locator assertions retry until the expected condition is met or
their timeout expires. That handles asynchronous UI changes better than reading
the state once or guessing a fixed sleep duration.

**Explanation and example:** After Add to cart, `expect(badge).to_have_text("1")`
waits for the badge to update. Slow motion is only a viewing aid, not a readiness
check. The original Python.org test uses a basic assert that does not retry.

## Why copy session-scoped test data before modifying it?

**Sample answer:** A session-scoped fixture's returned object is reused. Mutating
it can leak invalid data into later tests, creating order-dependent failures.

**Explanation and example:** Invalid-credential tests copy the credentials
dictionary before appending `_invalid` to one value. Our values are strings, so
a shallow dictionary copy is enough; nested mutable values would need more care.

## Why is checking the cart badge insufficient?

**Sample answer:** A count proves how many items the UI reports, but not their
identity, price, or quantity. I verify the cart contents as well as the badge.

**Explanation and example:** A badge of 1 could still accompany the wrong product.
Our addition test checks the backpack's name, $29.99 price, quantity, and row count.

## Why keep expected prices independent of the displayed value?

**Sample answer:** An assertion needs an independent expectation. Copying an actual
value and comparing it with itself can pass even when the displayed value is wrong.

**Explanation and example:** We explicitly expect the demo backpack to cost $29.99.
In a real product, the expected value should come from an approved requirement or
controlled test data and be updated when that requirement changes.

## Why verify an item exists before testing its removal?

**Sample answer:** Checking the starting state prevents a false positive where the
cart is empty because the item was never successfully added.

**Explanation and example:** The removal test adds its own backpack and checks the
cart row before clicking Remove. It never relies on the addition test running first.

## How does Arrange, Act, Assert help?

**Sample answer:** It makes the required starting state, behavior under test, and
expected outcome easy to distinguish. That improves readability and diagnosis.

**Explanation and example:** For removal, arrange means log in and add a backpack;
act means click Remove; assert means check the cart is empty and the badge absent.

## How can fixtures reuse setup without sharing login state?

**Sample answer:** Fixtures can request other fixtures. Function-scoped dependent
fixtures reuse instructions while executing those instructions for each test.

**Explanation and example:** `authenticated_page` requests `page` and credentials.
Each test gets a fresh context and performs login. We share the browser process
and credential values, not a logged-in page between tests.

## Why test a protected page after logout in the same context?

**Sample answer:** A redirect to login alone does not prove access was removed.
Reopening the protected URL checks that the previous context can no longer use it.

**Explanation and example:** Our logout test navigates directly to inventory.html
after logout and checks denial. Creating a new context would hide a stale-session
bug. This UI check does not prove server-side token revocation or API authorization.

## What can a trace show that a screenshot cannot?

**Sample answer:** A screenshot captures one state. A Playwright trace records
browser operations, page snapshots, screenshots, and network information over time.

**Explanation and example:** Trace Viewer helps inspect the actions before a cart
failure. Use the Python traceback too: traces do not record every Python assertion.
They can contain form data, so our generated reports remain local and Git-ignored.

## Why capture evidence before closing the context?

**Sample answer:** Closing releases pages and their live state. Screenshots must be
taken while the page is available, and tracing must be stopped to save its archive.

**Explanation and example:** Our page fixture saves evidence before context.close.
If a page has already crashed or closed, capture is best effort; diagnostic errors
should not replace the original test failure.

## How does an HTML report differ from screenshots and traces?

**Sample answer:** A report summarizes outcomes, durations, and failure output for
a run. Screenshots and traces provide evidence to investigate particular failures.

**Explanation and example:** `reports/report.html` is generated even for an entirely
passing run. Failure images and traces are stored separately when needed; they
are not currently embedded in the HTML report.

## Why can an application error message be a passing test?

**Sample answer:** Test success means the observed behavior matches the expected
behavior. Rejecting invalid input is often the correct result of a negative test.

**Explanation and example:** Six login cases intentionally reject credentials or
empty fields. They pass when the correct error appears and access stays blocked.
Only the valid-login case should open Products. Progress at 100% means execution
completed; the final summary tells us whether all those cases passed.
