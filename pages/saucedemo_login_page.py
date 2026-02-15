"""
SauceDemo Login Page Object.
Demonstrates AutoHeal with intentionally wrong selectors.
"""

from playwright.async_api import Page
from autoheal import AutoHealLocator
from pages.base_page import BasePage


class SauceDemoLoginPage(BasePage):
    """Login page for saucedemo.com with self-healing selectors."""

    URL = "https://www.saucedemo.com"

    # Intentionally WRONG selectors to demonstrate AutoHeal
    USERNAME_FIELD_WRONG = "#user-name-Wrong"
    PASSWORD_FIELD = "#password"
    LOGIN_BUTTON_WRONG = "#login-button-Wrong"

    # Correct selectors (for comparison)
    USERNAME_FIELD_CORRECT = "#user-name"
    LOGIN_BUTTON_CORRECT = "#login-button"

    # Error message selector
    ERROR_MESSAGE = "[data-test='error']"

    async def navigate(self):
        """Navigate to SauceDemo login page."""
        await self.page.goto(self.URL)

    async def get_username_input(self, use_wrong_selector: bool = True):
        """
        Get username input element.

        Args:
            use_wrong_selector: If True, uses intentionally wrong selector
                               to demonstrate AutoHeal capability.
        """
        selector = self.USERNAME_FIELD_WRONG if use_wrong_selector else self.USERNAME_FIELD_CORRECT
        return await self.autoheal.find_element_async(
            selector,
            "Username input field on SauceDemo login page"
        )

    async def get_password_input(self):
        """Get password input element."""
        return await self.autoheal.find_element_async(
            self.PASSWORD_FIELD,
            "Password input field on SauceDemo login page"
        )

    async def get_login_button(self, use_wrong_selector: bool = True):
        """
        Get login button element.

        Args:
            use_wrong_selector: If True, uses intentionally wrong selector
                               to demonstrate AutoHeal capability.
        """
        selector = self.LOGIN_BUTTON_WRONG if use_wrong_selector else self.LOGIN_BUTTON_CORRECT
        return await self.autoheal.find_element_async(
            selector,
            "Login button on SauceDemo login page"
        )

    async def login(self, username: str, password: str, use_wrong_selectors: bool = True):
        """
        Perform login action.

        Args:
            username: Username to enter.
            password: Password to enter.
            use_wrong_selectors: If True, uses wrong selectors to demonstrate healing.
        """
        username_input = await self.get_username_input(use_wrong_selectors)
        password_input = await self.get_password_input()
        login_button = await self.get_login_button(use_wrong_selectors)

        await username_input.fill(username)
        await password_input.fill(password)
        await login_button.click()

    async def get_error_message(self) -> str:
        """Get login error message text."""
        error_elem = await self.autoheal.find_element_async(
            self.ERROR_MESSAGE,
            "Error message on SauceDemo login page"
        )
        return await error_elem.text_content()

    async def is_error_displayed(self) -> bool:
        """Check if error message is displayed."""
        return await self.autoheal.is_element_present_async(
            self.ERROR_MESSAGE,
            "Error message on SauceDemo login page"
        )
