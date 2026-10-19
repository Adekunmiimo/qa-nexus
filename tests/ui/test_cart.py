from playwright.sync_api import Page, expect


def test_add_product_to_cart(authenticated_page: Page):
    # The fixture logs in independently for this test in a fresh context.
    # page is a local alias for readability; it is the same supplied Page object.
    page = authenticated_page

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


def test_remove_product_from_cart(authenticated_page: Page):
    # Login setup is reusable, but this test still adds its own item. It must
    # pass alone without relying on the add-to-cart test having run first.
    page = authenticated_page

    product_name = "Sauce Labs Backpack"
    product = page.locator('[data-test="inventory-item"]').filter(
        has=page.get_by_text(product_name, exact=True)
    )
    product.get_by_role("button", name="Add to cart", exact=True).click()
    badge = page.locator('[data-test="shopping-cart-badge"]')
    expect(badge).to_have_text("1")
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url("https://www.saucedemo.com/cart.html")

    # Prove the item exists before removal. Otherwise an empty cart could give
    # false confidence: there might never have been anything to remove.
    cart_items = page.locator('[data-test="inventory-item"]')
    expect(cart_items).to_have_count(1)
    cart_product = cart_items.filter(has=page.get_by_text(product_name, exact=True))
    expect(cart_product).to_have_count(1)

    # Act, then assert the resulting state. SauceDemo removes the badge entirely
    # when the cart is empty, rather than displaying a badge containing zero.
    cart_product.get_by_role("button", name="Remove", exact=True).click()
    expect(cart_items).to_have_count(0)
    expect(badge).to_have_count(0)
    expect(page).to_have_url("https://www.saucedemo.com/cart.html")

    # Navigate back through the UI to check the product card agrees with the cart.
    # Playwright locators find current elements after navigation, so product can
    # be reused here even though the original inventory page has been replaced.
    page.get_by_role("button", name="Continue Shopping", exact=True).click()
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
    expect(product.get_by_role("button", name="Add to cart", exact=True)).to_be_visible()
    expect(product.get_by_role("button", name="Remove", exact=True)).to_have_count(0)
    expect(badge).to_have_count(0)
