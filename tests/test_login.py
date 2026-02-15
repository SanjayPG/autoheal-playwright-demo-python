"""
Login tests demonstrating AutoHeal Locator with Playwright.
"""

import pytest
from pages.login_page import LoginPage


@pytest.mark.login
@pytest.mark.asyncio
async def test_successful_login(page, autoheal_locator):
    """Test successful login with valid credentials."""
   
    # Create page object
    login_page = LoginPage(page, autoheal_locator)
   
    # Navigate and login
    await login_page.navigate()
    await login_page.login("tomsmith", "SuperSecretPassword!")
   
    # Verify success
    assert await login_page.is_success_message_displayed(), \
        "Success message should be displayed after valid login"


@pytest.mark.login
@pytest.mark.asyncio
async def test_invalid_login(page, autoheal_locator):
    """Test login with invalid credentials."""
   
    login_page = LoginPage(page, autoheal_locator)
   
    await login_page.navigate()
    await login_page.login("invalid", "wrongpassword")
   
    # Verify error
    assert await login_page.is_error_message_displayed(), \
        "Error message should be displayed after invalid login"


@pytest.mark.login
@pytest.mark.healing
@pytest.mark.asyncio
async def test_login_with_broken_selector(page, autoheal_locator):
    """
    Demonstrate AutoHeal fixing a broken selector.
   
    This test intentionally uses a WRONG selector that AutoHeal will fix.
    """
   
    await page.goto("https://the-internet.herokuapp.com/login")
   
    # Use WRONG selector - AutoHeal will fix it!
    username = await autoheal_locator.find_element_async(
        "#username-WRONG-SELECTOR",  # This is intentionally wrong!
        "Username input field on login page"
    )
   
    # AutoHeal found it! Now we can interact
    await username.fill("tomsmith")
   
    # Continue with correct selectors
    password = await autoheal_locator.find_element_async(
        "#password",
        "Password input field"
    )
    await password.fill("SuperSecretPassword!")
   
    login_btn = await autoheal_locator.find_element_async(
        "button[type='submit']",
        "Login button"
    )
    await login_btn.click()
   
    # Verify success
    assert await autoheal_locator.is_element_present_async(
        ".flash.success",
        "Success message"
    )
