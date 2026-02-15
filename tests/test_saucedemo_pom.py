"""
SauceDemo tests using Page Object Model with AutoHeal.

Demonstrates:
- POM pattern with self-healing selectors
- Login flow with broken selectors (AutoHeal fixes them)
- Product interactions on inventory page
- Cache behavior across page objects
"""

import pytest
from pages.saucedemo_login_page import SauceDemoLoginPage
from pages.saucedemo_inventory_page import SauceDemoInventoryPage


@pytest.mark.pom
@pytest.mark.asyncio
async def test_login_with_correct_selectors(page, autoheal_locator):
    """Test login using correct selectors - no healing needed."""

    login_page = SauceDemoLoginPage(page, autoheal_locator)

    await login_page.navigate()
    await login_page.login("standard_user", "secret_sauce", use_wrong_selectors=False)

    # Verify we're on inventory page
    assert "/inventory" in page.url, "Should redirect to inventory after login"
    print("Login with correct selectors - SUCCESS!")


@pytest.mark.pom
@pytest.mark.healing
@pytest.mark.asyncio
async def test_login_with_broken_selectors(page, autoheal_locator):
    """Test login using broken selectors - AutoHeal will fix them."""

    login_page = SauceDemoLoginPage(page, autoheal_locator)

    await login_page.navigate()
    # use_wrong_selectors=True uses intentionally broken selectors
    await login_page.login("standard_user", "secret_sauce", use_wrong_selectors=True)

    # Verify login succeeded despite broken selectors
    assert "/inventory" in page.url, "AutoHeal should fix selectors and login should succeed"
    print("Login with BROKEN selectors - AutoHeal fixed them!")


@pytest.mark.pom
@pytest.mark.asyncio
async def test_invalid_login_shows_error(page, autoheal_locator):
    """Test that invalid credentials show error message."""

    login_page = SauceDemoLoginPage(page, autoheal_locator)

    await login_page.navigate()
    await login_page.login("invalid_user", "wrong_password", use_wrong_selectors=False)

    # Should stay on login page with error
    assert await login_page.is_error_displayed(), "Error message should be displayed"
    error_text = await login_page.get_error_message()
    assert "Username and password do not match" in error_text
    print(f"Invalid login error: {error_text}")


@pytest.mark.pom
@pytest.mark.asyncio
async def test_add_product_to_cart(page, autoheal_locator):
    """Test adding product to cart after login."""

    # Login first
    login_page = SauceDemoLoginPage(page, autoheal_locator)
    await login_page.navigate()
    await login_page.login("standard_user", "secret_sauce", use_wrong_selectors=False)

    # Now on inventory page
    inventory_page = SauceDemoInventoryPage(page, autoheal_locator)

    # Verify page title
    title = await inventory_page.get_page_title_text()
    assert title == "Products", f"Expected 'Products', got '{title}'"

    # Add backpack to cart
    await inventory_page.add_product_to_cart("sauce-labs-backpack")

    # Verify cart has 1 item
    cart_count = await inventory_page.get_cart_item_count()
    assert cart_count == 1, f"Expected 1 item in cart, got {cart_count}"
    print("Added Sauce Labs Backpack to cart - SUCCESS!")


@pytest.mark.pom
@pytest.mark.asyncio
async def test_add_multiple_products(page, autoheal_locator):
    """Test adding multiple products to cart."""

    # Login
    login_page = SauceDemoLoginPage(page, autoheal_locator)
    await login_page.navigate()
    await login_page.login("standard_user", "secret_sauce", use_wrong_selectors=False)

    # Add products
    inventory_page = SauceDemoInventoryPage(page, autoheal_locator)
    await inventory_page.add_product_to_cart("sauce-labs-backpack")
    await inventory_page.add_product_to_cart("sauce-labs-bike-light")
    await inventory_page.add_product_to_cart("sauce-labs-bolt-t-shirt")

    # Verify cart count
    cart_count = await inventory_page.get_cart_item_count()
    assert cart_count == 3, f"Expected 3 items in cart, got {cart_count}"
    print("Added 3 products to cart - SUCCESS!")


@pytest.mark.pom
@pytest.mark.asyncio
async def test_remove_product_from_cart(page, autoheal_locator):
    """Test removing product from cart."""

    # Login and add product
    login_page = SauceDemoLoginPage(page, autoheal_locator)
    await login_page.navigate()
    await login_page.login("standard_user", "secret_sauce", use_wrong_selectors=False)

    inventory_page = SauceDemoInventoryPage(page, autoheal_locator)
    await inventory_page.add_product_to_cart("sauce-labs-backpack")

    # Verify added
    assert await inventory_page.get_cart_item_count() == 1

    # Remove it
    await inventory_page.remove_product_from_cart("sauce-labs-backpack")

    # Verify removed
    cart_count = await inventory_page.get_cart_item_count()
    assert cart_count == 0, f"Expected 0 items after removal, got {cart_count}"
    print("Removed product from cart - SUCCESS!")


@pytest.mark.pom
@pytest.mark.asyncio
async def test_sort_products(page, autoheal_locator):
    """Test sorting products by different criteria."""

    # Login
    login_page = SauceDemoLoginPage(page, autoheal_locator)
    await login_page.navigate()
    await login_page.login("standard_user", "secret_sauce", use_wrong_selectors=False)

    inventory_page = SauceDemoInventoryPage(page, autoheal_locator)

    # Get initial product order
    initial_products = await inventory_page.get_all_product_names()
    print(f"Initial order: {initial_products[0]}")

    # Sort Z to A
    await inventory_page.select_sort_option("za")
    za_products = await inventory_page.get_all_product_names()
    print(f"After Z-A sort: {za_products[0]}")

    # Verify order changed
    assert za_products[0] != initial_products[0], "Product order should change after sorting"

    # Sort by price low to high
    await inventory_page.select_sort_option("lohi")
    lohi_products = await inventory_page.get_all_product_names()
    print(f"After Price Low-High: {lohi_products[0]}")

    print("Sorting products - SUCCESS!")


@pytest.mark.pom
@pytest.mark.healing
@pytest.mark.asyncio
async def test_full_flow_with_healing(page, autoheal_locator):
    """
    Full e-commerce flow with broken selectors.

    This test demonstrates AutoHeal fixing selectors throughout
    a complete user journey.
    """

    # Login with broken selectors
    login_page = SauceDemoLoginPage(page, autoheal_locator)
    await login_page.navigate()
    await login_page.login("standard_user", "secret_sauce", use_wrong_selectors=True)

    assert "/inventory" in page.url, "Should be on inventory page"

    # Browse and add products
    inventory_page = SauceDemoInventoryPage(page, autoheal_locator)

    # Get all products
    products = await inventory_page.get_all_product_names()
    print(f"Found {len(products)} products: {products[:3]}...")

    # Add first two products
    await inventory_page.add_product_to_cart("sauce-labs-backpack")
    await inventory_page.add_product_to_cart("sauce-labs-bike-light")

    # Check cart
    cart_count = await inventory_page.get_cart_item_count()
    assert cart_count == 2, f"Expected 2 items, got {cart_count}"

    print("Full e-commerce flow with healing - SUCCESS!")
