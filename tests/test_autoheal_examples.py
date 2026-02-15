"""
AutoHeal Examples Test Suite.
Demonstrates various AutoHeal patterns and capabilities.

Based on autoheal-example1.spec.ts and autoheal-example2.spec.ts from the TypeScript demo.
"""

import pytest
from playwright.async_api import Page

from autoheal import AutoHealLocator


class TestAutoHealBasicExamples:
    """Basic AutoHeal usage examples."""

    @pytest.mark.asyncio
    @pytest.mark.healing
    @pytest.mark.example
    async def test_autoheal_with_css_selector(
        self, page: Page, autoheal_locator: AutoHealLocator
    ):
        """
        Example: AutoHeal with CSS selector.

        Demonstrates using a wrong CSS selector that AutoHeal will fix.
        """
        await page.goto("https://www.saucedemo.com")

        # Using WRONG selector - AutoHeal will find the correct one
        username_elem = await autoheal_locator.find_element_async(
            "#user-name-BROKEN",  # Wrong selector
            "Username input field on login page"
        )

        await username_elem.fill("standard_user")
        value = await username_elem.input_value()
        assert value == "standard_user"

        print("\nAutoHeal successfully healed the broken CSS selector!")

    @pytest.mark.asyncio
    @pytest.mark.healing
    @pytest.mark.example
    async def test_autoheal_with_xpath_selector(
        self, page: Page, autoheal_locator: AutoHealLocator
    ):
        """
        Example: AutoHeal with XPath selector.

        Demonstrates using a wrong XPath selector that AutoHeal will fix.
        """
        await page.goto("https://www.saucedemo.com")

        # Using WRONG XPath - AutoHeal will find the correct one
        password_elem = await autoheal_locator.find_element_async(
            "//input[@id='password-wrong']",  # Wrong XPath
            "Password input field on login page"
        )

        await password_elem.fill("secret_sauce")
        value = await password_elem.input_value()
        assert value == "secret_sauce"

        print("\nAutoHeal successfully healed the broken XPath selector!")

    @pytest.mark.asyncio
    @pytest.mark.healing
    @pytest.mark.example
    async def test_autoheal_with_attribute_selector(
        self, page: Page, autoheal_locator: AutoHealLocator
    ):
        """
        Example: AutoHeal with attribute selector.

        Demonstrates healing a broken attribute-based selector.
        """
        await page.goto("https://www.saucedemo.com")

        # Wrong attribute selector
        login_btn = await autoheal_locator.find_element_async(
            "[data-test='login-btn']",  # Wrong - actual is 'login-button'
            "Login button"
        )

        # Verify it's a button we can click
        tag_name = await login_btn.evaluate("el => el.tagName")
        assert tag_name.lower() == "input", f"Expected input, got {tag_name}"

        print("\nAutoHeal successfully healed the broken attribute selector!")

    @pytest.mark.asyncio
    @pytest.mark.healing
    @pytest.mark.example
    async def test_autoheal_cache_hit(
        self, page: Page, autoheal_locator: AutoHealLocator
    ):
        """
        Example: AutoHeal caching behavior.

        First request heals the selector and caches it.
        Second request uses the cached selector (no AI call needed).
        """
        await page.goto("https://www.saucedemo.com")

        # First request - will heal and cache
        elem1 = await autoheal_locator.find_element_async(
            "#user-name-wrong",
            "Username input"
        )
        await elem1.fill("test1")

        # Reload page
        await page.reload()

        # Second request - should use cached selector
        elem2 = await autoheal_locator.find_element_async(
            "#user-name-wrong",  # Same broken selector
            "Username input"  # Same description
        )
        await elem2.fill("test2")

        # Check cache metrics
        cache_metrics = autoheal_locator.get_cache_metrics()
        print(f"\nCache hits: {cache_metrics.total_hits}")
        print(f"Cache misses: {cache_metrics.total_misses}")
        print(f"Hit rate: {cache_metrics.get_hit_rate():.1%}")

        # The second request should have been a cache hit
        assert cache_metrics.total_hits >= 1, "Expected at least one cache hit"


class TestAutoHealElementInteractions:
    """Tests demonstrating AutoHeal with various element interactions."""

    @pytest.mark.asyncio
    @pytest.mark.healing
    @pytest.mark.example
    async def test_autoheal_fill_and_clear(
        self, page: Page, autoheal_locator: AutoHealLocator
    ):
        """Test filling and clearing an input field with healed selector."""
        await page.goto("https://www.saucedemo.com")

        elem = await autoheal_locator.find_element_async(
            "#username-broken",  # Wrong
            "Username input"
        )

        # Fill
        await elem.fill("hello")
        assert await elem.input_value() == "hello"

        # Clear by filling empty
        await elem.fill("")
        assert await elem.input_value() == ""

        print("\nFill and clear operations successful with healed selector!")

    @pytest.mark.asyncio
    @pytest.mark.healing
    @pytest.mark.example
    async def test_autoheal_click_interaction(
        self, page: Page, autoheal_locator: AutoHealLocator
    ):
        """Test click interaction with healed selector."""
        await page.goto("https://www.saucedemo.com")

        # First log in
        username = await autoheal_locator.find_element_async("#user-name", "Username")
        password = await autoheal_locator.find_element_async("#password", "Password")
        await username.fill("standard_user")
        await password.fill("secret_sauce")

        # Click with healed selector
        login_btn = await autoheal_locator.find_element_async(
            "#login-btn-wrong",  # Wrong selector
            "Login button"
        )
        await login_btn.click()

        await page.wait_for_timeout(1000)

        # Verify we navigated
        title = await autoheal_locator.find_element_async(".title", "Page title")
        title_text = await title.text_content()
        assert title_text == "Products"

        print("\nClick interaction successful with healed selector!")

    @pytest.mark.asyncio
    @pytest.mark.healing
    @pytest.mark.example
    async def test_autoheal_find_multiple_elements(
        self, page: Page, autoheal_locator: AutoHealLocator
    ):
        """Test finding multiple elements with AutoHeal."""
        await page.goto("https://www.saucedemo.com")

        # Log in first
        username = await autoheal_locator.find_element_async("#user-name", "Username")
        password = await autoheal_locator.find_element_async("#password", "Password")
        login_btn = await autoheal_locator.find_element_async("#login-button", "Login")

        await username.fill("standard_user")
        await password.fill("secret_sauce")
        await login_btn.click()
        await page.wait_for_timeout(1000)

        # Find multiple product items
        items = await autoheal_locator.find_elements_async(
            ".inventory_item",
            "Inventory items"
        )

        assert len(items) == 6, f"Expected 6 inventory items, got {len(items)}"
        print(f"\nFound {len(items)} inventory items!")


class TestAutoHealElementPresence:
    """Tests for checking element presence with AutoHeal."""

    @pytest.mark.asyncio
    @pytest.mark.healing
    @pytest.mark.example
    async def test_is_element_present_true(
        self, page: Page, autoheal_locator: AutoHealLocator
    ):
        """Test is_element_present returns True for existing element."""
        await page.goto("https://www.saucedemo.com")

        is_present = await autoheal_locator.is_element_present_async(
            "#user-name",
            "Username input"
        )

        assert is_present is True, "Expected username input to be present"
        print("\nis_element_present correctly returned True!")

    @pytest.mark.asyncio
    @pytest.mark.healing
    @pytest.mark.example
    async def test_is_element_present_false(
        self, page: Page, autoheal_locator: AutoHealLocator
    ):
        """Test is_element_present returns False for non-existent element."""
        await page.goto("https://www.saucedemo.com")

        is_present = await autoheal_locator.is_element_present_async(
            "#completely-nonexistent-element-xyz123",
            "Nonexistent element"
        )

        assert is_present is False, "Expected nonexistent element to not be present"
        print("\nis_element_present correctly returned False for nonexistent element!")


class TestAutoHealLoginFlow:
    """Complete login flow tests demonstrating real-world AutoHeal usage."""

    @pytest.mark.asyncio
    @pytest.mark.healing
    @pytest.mark.example
    async def test_complete_login_flow_with_healing(
        self, page: Page, autoheal_locator: AutoHealLocator
    ):
        """
        Complete login and add to cart flow with healing.

        Based on autoheal-example1.spec.ts from TypeScript demo.
        Uses intentionally wrong selectors that AutoHeal will fix.
        """
        await page.goto("https://www.saucedemo.com")

        # Username with correct selector
        username_locator = await autoheal_locator.find_element_async(
            "#user-name",  # Correct selector
            "Username input field"
        )
        await username_locator.fill("standard_user")

        # Password with WRONG selector - AutoHeal will fix
        password_locator = await autoheal_locator.find_element_async(
            "#pwd",  # Wrong - should be #password
            "Password input field"
        )
        await password_locator.fill("secret_sauce")

        # Login button with WRONG selector - AutoHeal will fix
        login_button = await autoheal_locator.find_element_async(
            "#submit-btn",  # Wrong - should be #login-button
            "Login button"
        )
        await login_button.click()

        await page.wait_for_timeout(2000)

        # Verify Products page title
        product_title = await autoheal_locator.find_element_async(
            ".title",
            "Products page title"
        )
        title_text = await product_title.text_content()
        assert "Products" in title_text, f"Expected 'Products' in title, got '{title_text}'"

        print("\nComplete login flow with healing passed!")

    @pytest.mark.asyncio
    @pytest.mark.healing
    @pytest.mark.example
    async def test_add_to_cart_after_login(
        self, page: Page, autoheal_locator: AutoHealLocator
    ):
        """Test adding product to cart after logging in."""
        await page.goto("https://www.saucedemo.com")

        # Login
        username = await autoheal_locator.find_element_async("#user-name", "Username")
        password = await autoheal_locator.find_element_async("#password", "Password")
        login_btn = await autoheal_locator.find_element_async("#login-button", "Login")

        await username.fill("standard_user")
        await password.fill("secret_sauce")
        await login_btn.click()
        await page.wait_for_timeout(1000)

        # Add backpack to cart
        add_btn = await autoheal_locator.find_element_async(
            "[data-test='add-to-cart-sauce-labs-backpack']",
            "Add backpack to cart button"
        )
        await add_btn.click()
        await page.wait_for_timeout(500)

        # Verify cart badge shows 1
        cart_badge = await autoheal_locator.find_element_async(
            ".shopping_cart_badge",
            "Shopping cart badge"
        )
        badge_text = await cart_badge.text_content()
        assert badge_text == "1", f"Expected '1' in cart badge, got '{badge_text}'"

        print("\nAdd to cart test passed!")


class TestAutoHealMetrics:
    """Tests demonstrating AutoHeal metrics collection."""

    @pytest.mark.asyncio
    @pytest.mark.healing
    @pytest.mark.example
    async def test_metrics_collection(
        self, page: Page, autoheal_locator: AutoHealLocator
    ):
        """Test that metrics are properly collected during healing."""
        await page.goto("https://www.saucedemo.com")

        # Perform some operations
        elem1 = await autoheal_locator.find_element_async("#user-name", "Username")
        await elem1.fill("test")

        elem2 = await autoheal_locator.find_element_async("#password", "Password")
        await elem2.fill("test")

        # Get metrics
        metrics = autoheal_locator.get_metrics()
        cache_metrics = autoheal_locator.get_cache_metrics()

        print(f"\nMetrics Report:")
        print(f"  Total requests: {metrics.total_requests}")
        print(f"  Successful: {metrics.successful_requests}")
        print(f"  Failed: {metrics.total_requests - metrics.successful_requests}")
        print(f"  Success rate: {metrics.get_success_rate():.1%}")
        print(f"\nCache Metrics:")
        print(f"  Hits: {cache_metrics.total_hits}")
        print(f"  Misses: {cache_metrics.total_misses}")
        print(f"  Hit rate: {cache_metrics.get_hit_rate():.1%}")

        assert metrics.total_requests >= 2, "Expected at least 2 requests"
        assert metrics.successful_requests >= 2, "Expected at least 2 successful requests"

    @pytest.mark.asyncio
    @pytest.mark.healing
    @pytest.mark.example
    async def test_health_status(
        self, page: Page, autoheal_locator: AutoHealLocator
    ):
        """Test health status reporting."""
        await page.goto("https://www.saucedemo.com")

        # Perform an operation
        elem = await autoheal_locator.find_element_async("#user-name", "Username")
        await elem.fill("test")

        # Get health status
        health = autoheal_locator.get_health_status()

        print(f"\nHealth Status:")
        print(f"  Status: {health}")

        # Health should indicate the system is working
        assert health is not None, "Expected health status to be available"
