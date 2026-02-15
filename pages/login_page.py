"""Login Page Object with AutoHeal."""

from playwright.async_api import Page
from autoheal import AutoHealLocator
from .base_page import BasePage


class LoginPage(BasePage):
    """Login page object."""
   
    URL = "https://the-internet.herokuapp.com/login"
   
    # Selectors
    USERNAME_FIELD = "#username"
    PASSWORD_FIELD = "#password"
    LOGIN_BUTTON = "button[type='submit']"
    SUCCESS_MESSAGE = ".flash.success"
    ERROR_MESSAGE = ".flash.error"
   
    def __init__(self, page: Page, autoheal: AutoHealLocator):
        super().__init__(page, autoheal)
   
    async def navigate(self):
        """Navigate to login page."""
        await self.page.goto(self.URL)
   
    async def login(self, username: str, password: str):
        """Perform login with AutoHeal."""
        # Find username field
        username_elem = await self.autoheal.find_element_async(
            self.USERNAME_FIELD,
            "Username input field on login page"
        )
        await username_elem.fill(username)
       
        # Find password field
        password_elem = await self.autoheal.find_element_async(
            self.PASSWORD_FIELD,
            "Password input field on login page"
        )
        await password_elem.fill(password)
       
        # Click login button
        login_btn = await self.autoheal.find_element_async(
            self.LOGIN_BUTTON,
            "Login submit button"
        )
        await login_btn.click()
   
    async def is_success_message_displayed(self) -> bool:
        """Check if success message is displayed."""
        return await self.autoheal.is_element_present_async(
            self.SUCCESS_MESSAGE,
            "Success flash message"
        )
   
    async def is_error_message_displayed(self) -> bool:
        """Check if error message is displayed."""
        return await self.autoheal.is_element_present_async(
            self.ERROR_MESSAGE,
            "Error flash message"
        )
