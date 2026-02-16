"""
Test demonstrating the quickstart setup for AutoHeal.

This test shows the simplest way to get started with AutoHeal:
1. Set your API key as an environment variable
2. Import get_autoheal_config from autoheal
3. Create the locator and start healing!

No custom config file needed - just set GROQ_API_KEY (or another provider's key)
and you're ready to go.
"""

import pytest
from playwright.async_api import Page

from autoheal import get_autoheal_config
from autoheal.impl.adapter import PlaywrightWebAutomationAdapter
from autoheal.reporting import ReportingAutoHealLocator


@pytest.fixture(scope="function")
def quickstart_locator(page: Page):
    """
    Quickstart fixture - minimal setup using built-in config.

    Just set one of these environment variables:
        - GROQ_API_KEY (FREE - recommended)
        - OPENAI_API_KEY
        - GEMINI_API_KEY
        - AUTOHEAL_API_URL (for local models)
    """
    config = get_autoheal_config()
    adapter = PlaywrightWebAutomationAdapter(page)
    locator = ReportingAutoHealLocator(adapter, config)

    yield locator

    # Print summary
    metrics = locator.autoheal.get_metrics()
    print(f"\nAutoHeal: {metrics.successful_requests}/{metrics.total_requests} successful")


@pytest.mark.quickstart
@pytest.mark.asyncio
async def test_quickstart_heal_selector(page: Page, quickstart_locator):
    """
    Quickstart example: Heal a broken CSS selector.

    This test uses the built-in get_autoheal_config() which auto-detects
    your AI provider from environment variables. No config file needed!
    """
    await page.goto("https://www.saucedemo.com")

    # This selector is WRONG - AutoHeal will fix it
    username = await quickstart_locator.find_element_async(
        "#user-name-BROKEN",
        "Username input field"
    )

    await username.fill("standard_user")
    value = await username.input_value()
    assert value == "standard_user"
    print("Quickstart healing works!")


@pytest.mark.quickstart
@pytest.mark.asyncio
async def test_quickstart_heal_native_locator(page: Page, quickstart_locator):
    """
    Quickstart example: Heal a broken Playwright native locator.
    """
    await page.goto("https://www.saucedemo.com")

    # This native locator has wrong name - AutoHeal will fix it
    password = await quickstart_locator.find_async(
        page.get_by_role("textbox", name="Password-WRONG"),
        "Password input field"
    )

    await password.fill("secret_sauce")
    value = await password.input_value()
    assert value == "secret_sauce"
    print("Quickstart native locator healing works!")


@pytest.mark.quickstart
@pytest.mark.asyncio
async def test_quickstart_full_login_flow(page: Page, quickstart_locator):
    """
    Quickstart example: Complete login flow with multiple broken selectors.

    Demonstrates that AutoHeal caches healed selectors, so the second
    time a selector is used, it's instant (no AI call needed).
    """
    await page.goto("https://www.saucedemo.com")

    # All these selectors are WRONG - AutoHeal fixes them
    username = await quickstart_locator.find_element_async(
        "#username-field-broken",
        "Username input on SauceDemo login"
    )
    await username.fill("standard_user")

    password = await quickstart_locator.find_element_async(
        "#password-field-broken",
        "Password input on SauceDemo login"
    )
    await password.fill("secret_sauce")

    login_btn = await quickstart_locator.find_element_async(
        "#login-btn-broken",
        "Login button on SauceDemo"
    )
    await login_btn.click()

    # Verify login succeeded
    await page.wait_for_url("**/inventory.html", timeout=5000)
    assert "inventory" in page.url
    print("Quickstart full login flow works!")


@pytest.mark.quickstart
@pytest.mark.asyncio
async def test_quickstart_native_locators_full_login(page: Page, quickstart_locator):
    """
    Quickstart example: Complete login flow using Playwright native locators.

    Uses get_by_role, get_by_placeholder - all with WRONG values
    that AutoHeal will fix automatically.
    """
    await page.goto("https://www.saucedemo.com")

    # WRONG role name - AutoHeal fixes it
    username = await quickstart_locator.find_async(
        page.get_by_role("textbox", name="Username-BROKEN"),
        "Username input field on SauceDemo login page"
    )
    await username.fill("standard_user")

    # WRONG placeholder - AutoHeal fixes it
    password = await quickstart_locator.find_async(
        page.get_by_placeholder("Password-BROKEN"),
        "Password input field on SauceDemo login page"
    )
    await password.fill("secret_sauce")

    # WRONG button name - AutoHeal fixes it
    login_btn = await quickstart_locator.find_async(
        page.get_by_role("button", name="Sign In"),
        "Login button on SauceDemo login page"
    )
    await login_btn.click()

    # Verify login succeeded
    await page.wait_for_url("**/inventory.html", timeout=5000)
    assert "inventory" in page.url
    print("Quickstart native locators full login works!")


@pytest.mark.quickstart
@pytest.mark.asyncio
async def test_quickstart_native_locators_add_to_cart(page: Page, quickstart_locator):
    """
    Quickstart example: Login and add item to cart using native locators.

    Demonstrates healing of various Playwright locator types in a real flow.
    """
    # Login first (using correct locators to speed up test)
    await page.goto("https://www.saucedemo.com")

    username = await quickstart_locator.find_async(
        page.get_by_role("textbox", name="Username"),
        "Username input"
    )
    await username.fill("standard_user")

    password = await quickstart_locator.find_async(
        page.get_by_role("textbox", name="Password"),
        "Password input"
    )
    await password.fill("secret_sauce")

    login_btn = await quickstart_locator.find_async(
        page.get_by_role("button", name="Login"),
        "Login button"
    )
    await login_btn.click()

    await page.wait_for_url("**/inventory.html", timeout=5000)

    # WRONG button text - AutoHeal fixes it
    add_to_cart_btn = await quickstart_locator.find_async(
        page.get_by_role("button", name="Add to cart - BROKEN"),
        "Add to cart button for first product on inventory page"
    )
    await add_to_cart_btn.click()

    # WRONG link - AutoHeal fixes it
    cart_link = await quickstart_locator.find_async(
        page.get_by_role("link", name="Cart-BROKEN"),
        "Shopping cart link in header"
    )
    await cart_link.click()

    # Verify item in cart
    await page.wait_for_url("**/cart.html", timeout=5000)
    assert "cart" in page.url
    print("Quickstart native locators add to cart works!")
