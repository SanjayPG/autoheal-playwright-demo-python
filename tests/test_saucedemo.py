"""
SauceDemo Test Suite with AutoHeal.
Demonstrates self-healing element location with intentionally wrong selectors.
"""

import pytest
from playwright.async_api import Page, expect

from pages.saucedemo_login_page import SauceDemoLoginPage
from pages.saucedemo_inventory_page import SauceDemoInventoryPage
from autoheal import AutoHealLocator


class TestSauceDemoLogin:
    """Login tests for SauceDemo with AutoHeal."""

    @pytest.mark.asyncio
    @pytest.mark.saucedemo
    @pytest.mark.login
    async def test_successful_login(self, page: Page, autoheal_locator: AutoHealLocator):
        """Test successful login with valid credentials."""
        login_page = SauceDemoLoginPage(page, autoheal_locator)
        inventory_page = SauceDemoInventoryPage(page, autoheal_locator)

        await login_page.navigate()
        # Using wrong selectors - AutoHeal will fix them
        await login_page.login("standard_user", "secret_sauce", use_wrong_selectors=True)

        # Wait for navigation
        await page.wait_for_timeout(1000)

        # Verify we're on the inventory page
        title_text = await inventory_page.get_page_title_text()
        assert title_text == "Products", f"Expected 'Products', got '{title_text}'"

    @pytest.mark.asyncio
    @pytest.mark.saucedemo
    @pytest.mark.login
    async def test_login_with_correct_selectors(self, page: Page, autoheal_locator: AutoHealLocator):
        """Test login using correct selectors (no healing needed)."""
        login_page = SauceDemoLoginPage(page, autoheal_locator)
        inventory_page = SauceDemoInventoryPage(page, autoheal_locator)

        await login_page.navigate()
        # Using correct selectors - no healing needed
        await login_page.login("standard_user", "secret_sauce", use_wrong_selectors=False)

        await page.wait_for_timeout(1000)

        title_text = await inventory_page.get_page_title_text()
        assert title_text == "Products"

    @pytest.mark.asyncio
    @pytest.mark.saucedemo
    @pytest.mark.login
    async def test_invalid_login(self, page: Page, autoheal_locator: AutoHealLocator):
        """Test login with invalid credentials shows error."""
        login_page = SauceDemoLoginPage(page, autoheal_locator)

        await login_page.navigate()
        await login_page.login("invalid_user", "wrong_password", use_wrong_selectors=True)

        await page.wait_for_timeout(500)

        # Verify error message is displayed
        assert await login_page.is_error_displayed(), "Expected error message to be displayed"
        error_text = await login_page.get_error_message()
        assert "Username and password do not match" in error_text or "locked out" in error_text.lower()

    @pytest.mark.asyncio
    @pytest.mark.saucedemo
    @pytest.mark.login
    async def test_locked_out_user(self, page: Page, autoheal_locator: AutoHealLocator):
        """Test that locked out user cannot login."""
        login_page = SauceDemoLoginPage(page, autoheal_locator)

        await login_page.navigate()
        await login_page.login("locked_out_user", "secret_sauce", use_wrong_selectors=True)

        await page.wait_for_timeout(500)

        assert await login_page.is_error_displayed()
        error_text = await login_page.get_error_message()
        assert "locked out" in error_text.lower()


class TestSauceDemoInventory:
    """Inventory page tests for SauceDemo with AutoHeal."""

    @pytest.fixture
    async def logged_in_page(self, page: Page, autoheal_locator: AutoHealLocator):
        """Fixture to log in before inventory tests."""
        login_page = SauceDemoLoginPage(page, autoheal_locator)
        await login_page.navigate()
        await login_page.login("standard_user", "secret_sauce", use_wrong_selectors=True)
        await page.wait_for_timeout(1000)
        return page

    @pytest.mark.asyncio
    @pytest.mark.saucedemo
    @pytest.mark.cart
    async def test_add_product_to_cart(
        self, logged_in_page: Page, autoheal_locator: AutoHealLocator
    ):
        """Test adding a product to cart."""
        inventory_page = SauceDemoInventoryPage(logged_in_page, autoheal_locator)

        # Initial cart should be empty
        initial_count = await inventory_page.get_cart_item_count()
        assert initial_count == 0, f"Expected empty cart, got {initial_count}"

        # Add backpack to cart
        await inventory_page.add_product_to_cart("sauce-labs-backpack")
        await logged_in_page.wait_for_timeout(500)

        # Verify cart count increased
        new_count = await inventory_page.get_cart_item_count()
        assert new_count == 1, f"Expected 1 item in cart, got {new_count}"

    @pytest.mark.asyncio
    @pytest.mark.saucedemo
    @pytest.mark.cart
    async def test_add_multiple_products(
        self, logged_in_page: Page, autoheal_locator: AutoHealLocator
    ):
        """Test adding multiple products to cart."""
        inventory_page = SauceDemoInventoryPage(logged_in_page, autoheal_locator)

        # Add multiple products
        await inventory_page.add_product_to_cart("sauce-labs-backpack")
        await inventory_page.add_product_to_cart("sauce-labs-bike-light")
        await inventory_page.add_product_to_cart("sauce-labs-bolt-t-shirt")
        await logged_in_page.wait_for_timeout(500)

        # Verify cart count
        count = await inventory_page.get_cart_item_count()
        assert count == 3, f"Expected 3 items in cart, got {count}"

    @pytest.mark.asyncio
    @pytest.mark.saucedemo
    @pytest.mark.cart
    async def test_remove_product_from_cart(
        self, logged_in_page: Page, autoheal_locator: AutoHealLocator
    ):
        """Test removing a product from cart."""
        inventory_page = SauceDemoInventoryPage(logged_in_page, autoheal_locator)

        # Add product first
        await inventory_page.add_product_to_cart("sauce-labs-backpack")
        await logged_in_page.wait_for_timeout(500)
        assert await inventory_page.get_cart_item_count() == 1

        # Remove the product
        await inventory_page.remove_product_from_cart("sauce-labs-backpack")
        await logged_in_page.wait_for_timeout(500)

        # Verify cart is empty
        count = await inventory_page.get_cart_item_count()
        assert count == 0, f"Expected 0 items in cart, got {count}"

    @pytest.mark.asyncio
    @pytest.mark.saucedemo
    async def test_get_all_products(
        self, logged_in_page: Page, autoheal_locator: AutoHealLocator
    ):
        """Test retrieving all product names."""
        inventory_page = SauceDemoInventoryPage(logged_in_page, autoheal_locator)

        product_names = await inventory_page.get_all_product_names()

        # SauceDemo has 6 products
        assert len(product_names) == 6, f"Expected 6 products, got {len(product_names)}"
        assert "Sauce Labs Backpack" in product_names
        assert "Sauce Labs Bike Light" in product_names

    @pytest.mark.asyncio
    @pytest.mark.saucedemo
    async def test_sort_products_by_price(
        self, logged_in_page: Page, autoheal_locator: AutoHealLocator
    ):
        """Test sorting products by price low to high."""
        inventory_page = SauceDemoInventoryPage(logged_in_page, autoheal_locator)

        # Sort by price low to high
        await inventory_page.select_sort_option("lohi")
        await logged_in_page.wait_for_timeout(500)

        # Get product names after sorting
        product_names = await inventory_page.get_all_product_names()

        # First product should be the cheapest (Sauce Labs Onesie at $7.99)
        assert product_names[0] == "Sauce Labs Onesie", \
            f"Expected 'Sauce Labs Onesie' first, got '{product_names[0]}'"


class TestSauceDemoHealing:
    """Tests specifically demonstrating AutoHeal self-healing capability."""

    @pytest.mark.asyncio
    @pytest.mark.saucedemo
    @pytest.mark.healing
    async def test_healing_with_wrong_username_selector(
        self, page: Page, autoheal_locator: AutoHealLocator
    ):
        """
        Test that AutoHeal heals a completely wrong username selector.

        This test uses '#user-name-Wrong' which doesn't exist.
        AutoHeal should automatically find the correct '#user-name' selector.
        """
        login_page = SauceDemoLoginPage(page, autoheal_locator)
        await login_page.navigate()

        # This uses the WRONG selector '#user-name-Wrong'
        # AutoHeal should heal it to '#user-name'
        username_elem = await login_page.get_username_input(use_wrong_selector=True)

        # If we got here, healing worked - verify we can interact with the element
        await username_elem.fill("test_user")

        # Get the value to verify it was filled
        value = await username_elem.input_value()
        assert value == "test_user", f"Expected 'test_user', got '{value}'"

    @pytest.mark.asyncio
    @pytest.mark.saucedemo
    @pytest.mark.healing
    async def test_healing_with_wrong_button_selector(
        self, page: Page, autoheal_locator: AutoHealLocator
    ):
        """
        Test that AutoHeal heals a wrong login button selector.

        Uses '#login-button-Wrong' which doesn't exist.
        AutoHeal should find the correct '#login-button'.
        """
        login_page = SauceDemoLoginPage(page, autoheal_locator)
        await login_page.navigate()

        # Fill login form first
        username_elem = await login_page.get_username_input(use_wrong_selector=False)
        password_elem = await login_page.get_password_input()
        await username_elem.fill("standard_user")
        await password_elem.fill("secret_sauce")

        # This uses the WRONG selector '#login-button-Wrong'
        # AutoHeal should heal it to '#login-button'
        login_button = await login_page.get_login_button(use_wrong_selector=True)

        # If we got here, healing worked - click the button
        await login_button.click()
        await page.wait_for_timeout(1000)

        # Verify navigation happened (we're on inventory page)
        inventory_page = SauceDemoInventoryPage(page, autoheal_locator)
        title_text = await inventory_page.get_page_title_text()
        assert title_text == "Products"

    @pytest.mark.asyncio
    @pytest.mark.saucedemo
    @pytest.mark.healing
    async def test_complete_flow_with_healing(
        self, page: Page, autoheal_locator: AutoHealLocator
    ):
        """
        End-to-end test demonstrating healing throughout a complete user flow.

        Uses wrong selectors for both username and login button,
        demonstrating AutoHeal working across multiple elements.
        """
        login_page = SauceDemoLoginPage(page, autoheal_locator)
        inventory_page = SauceDemoInventoryPage(page, autoheal_locator)

        # Navigate to login
        await login_page.navigate()

        # Login with healing (wrong selectors)
        await login_page.login("standard_user", "secret_sauce", use_wrong_selectors=True)
        await page.wait_for_timeout(1000)

        # Verify on inventory page
        title_text = await inventory_page.get_page_title_text()
        assert title_text == "Products"

        # Add items to cart
        await inventory_page.add_product_to_cart("sauce-labs-backpack")
        await inventory_page.add_product_to_cart("sauce-labs-bike-light")
        await page.wait_for_timeout(500)

        # Verify cart
        count = await inventory_page.get_cart_item_count()
        assert count == 2, f"Expected 2 items in cart, got {count}"

        print("\nComplete flow with healing passed successfully!")
