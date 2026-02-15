"""
Parallel healing tests - multiple tests sharing a single report.

All healed selectors will appear in one consolidated report.

Run with: pytest tests/test_parallel_heal.py -v
"""

import pytest


@pytest.mark.healing
@pytest.mark.asyncio
async def test_heal_username_field(page, autoheal_locator):
    """Test 1: Heal broken username selector."""

    await page.goto("https://www.saucedemo.com")

    # WRONG selector: actual id is "user-name"
    username = await autoheal_locator.find_element_async(
        "#user-name-BROKEN",
        "Username input field on the SauceDemo login page"
    )

    await username.fill("standard_user")
    value = await username.input_value()
    assert value == "standard_user", f"Expected 'standard_user', got '{value}'"
    print("Test 1: Healed #user-name-BROKEN successfully!")


@pytest.mark.healing
@pytest.mark.asyncio
async def test_heal_password_field(page, autoheal_locator):
    """Test 2: Heal broken password selector."""

    await page.goto("https://www.saucedemo.com")

    # WRONG selector: actual id is "password"
    password = await autoheal_locator.find_element_async(
        "#password-WRONG",
        "Password input field on the SauceDemo login page"
    )

    await password.fill("secret_sauce")
    value = await password.input_value()
    assert value == "secret_sauce", f"Expected 'secret_sauce', got '{value}'"

    username = await autoheal_locator.find_element_async(
        "#user-name-BROKEN",
        "Username input field on the SauceDemo login page"
    )

    await username.fill("standard_user")

    print("Test 2: Healed #password-WRONG successfully!")