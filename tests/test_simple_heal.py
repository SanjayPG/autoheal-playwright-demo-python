"""
Simple tests to verify AutoHeal works with both string selectors and native
Playwright Locators.

Uses intentionally WRONG selectors/locators that the AI should heal.
"""

import pytest


@pytest.mark.healing
@pytest.mark.asyncio
async def test_heal_broken_selector(page, autoheal_locator):
    """AutoHeal should fix a broken CSS selector using the AI."""

    autoheal_locator.clear_cache()
    await page.goto("https://www.saucedemo.com")

    # WRONG selector: actual id is "user-name"
    username = await autoheal_locator.find_element_async(
        "#user-name-BROKEN",
        "Username input field on the SauceDemo login page"
    )

    await username.fill("standard_user")
    value = await username.input_value()
    assert value == "standard_user", f"Expected 'standard_user', got '{value}'"
    print("Healed #user-name-BROKEN -> element found and filled successfully!")





@pytest.mark.healing
@pytest.mark.asyncio
async def test_heal_broken_native_locator(page, autoheal_locator):
    """AutoHeal should fix a broken native Playwright locator using the AI."""

    await page.goto("https://www.saucedemo.com")

    # WRONG native locator: there is no textbox with name "Username-BROKEN"
    username = await autoheal_locator.find_async(
        page.get_by_role("textbox", name="Username"),
        "Username input field on the SauceDemo login page"
    )

    # Result is a native Playwright Locator - use Locator API directly
    await username.fill("standard_user")
    value = await username.input_value()
    assert value == "standard_user", f"Expected 'standard_user', got '{value}'"
    print("Healed native locator -> username field found and filled successfully!")

    # WRONG native locator: there is no textbox with name "Password-BROKEN"
    password = await autoheal_locator.find_async(
        page.get_by_role("textbox", name="Password-BROKEN"),
        "Password input field on the SauceDemo login page"
    )

    await password.fill("secret_sauce")
    password_value = await password.input_value()
    assert password_value == "secret_sauce", f"Expected 'secret_sauce', got '{password_value}'"
    print("Healed native locator -> password field found and filled successfully!")

    # WRONG native locator: there is no button with name "Login-BROKEN"
    login_button = await autoheal_locator.find_async(
        page.get_by_role("button", name="Login-BROKEN"),
        "Login button on the SauceDemo login page"
    )

    await login_button.click()
    # Verify login was successful by checking we're on the inventory page
    await page.wait_for_url("**/inventory.html", timeout=5000)
    print("Healed native locator -> login button found and clicked successfully!")


@pytest.mark.healing
@pytest.mark.asyncio
async def test_find_async_correct_locator(page, autoheal_locator):
    """find_async() should return the original locator when it already works."""

    await page.goto("https://www.saucedemo.com")

    # Correct native locator - should work without healing
    login_button = await autoheal_locator.find_async(
        page.get_by_role("button", name="Login"),
        "Login button on the SauceDemo login page"
    )

    # Verify it's a working native Locator
    assert await login_button.count() == 1
    assert await login_button.is_visible()
    print("find_async() returned correct native locator without healing!")
