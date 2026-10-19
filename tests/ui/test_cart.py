from playwright.sync_api import Page, expect


def test_add_product_to_cart(page: Page, credentials: dict[str, str]):
    # This workflow logs in for itself: it must not depend on a login test
    # running first. The page fixture provides a fresh browser context.
    page.get_by_placeholder("Username", exact=True).fill(credentials["username"])
    page.get_by_placeholder("Password", exact=True).fill(credentials["password"])
    page.get_by_role("button", name="Login", exact=True).click()
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")

    # Fixed expected values describe the behavior we want to prove. Reading the
    # expected price from the UI would allow an incorrect price to pass the test.
    product_name = "Sauce Labs Backpack"
    expected_price = "$29.99"

    # SauceDemo supplies data-test attributes for containers without useful
    # accessible roles. These avoid depending on layout or styling classes.
    # filter(has=...) selects the card containing this product's exact name,
    # so the button and price checks cannot accidentally target another item.
    product = page.locator('[data-test="inventory-item"]').filter(
        has=page.get_by_text(product_name, exact=True)
    )
    expect(product).to_have_count(1)
    expect(product.get_by_text(product_name, exact=True)).to_be_visible()
    expect(product.locator('[data-test="inventory-item-price"]')).to_have_text(
        expected_price
    )

    # Verify the starting state, then the visible changes caused by adding.
    badge = page.locator('[data-test="shopping-cart-badge"]')
    expect(badge).to_have_count(0)
    product.get_by_role("button", name="Add to cart", exact=True).click()
    expect(product.get_by_role("button", name="Remove", exact=True)).to_be_visible()
    expect(badge).to_have_text("1")

    # The cart icon has no descriptive accessible name, so use its test attribute.
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url("https://www.saucedemo.com/cart.html")
    expect(page.get_by_text("Your Cart", exact=True)).to_be_visible()

    # Check exactly one cart row, then its identity, price, and quantity.
    # A badge alone would not prove that the correct product reached the cart.
    cart_items = page.locator('[data-test="inventory-item"]')
    expect(cart_items).to_have_count(1)
    expect(cart_items.get_by_text(product_name, exact=True)).to_be_visible()
    expect(cart_items.locator('[data-test="inventory-item-price"]')).to_have_text(
        expected_price
    )
    expect(cart_items.locator('[data-test="item-quantity"]')).to_have_text("1")
