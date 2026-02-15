"""
Base Page Object for all page objects.
Provides common functionality using AutoHeal Locator.
"""

from playwright.async_api import Page
from autoheal import AutoHealLocator


class BasePage:
    """Base page object with AutoHeal integration."""
   
    def __init__(self, page: Page, autoheal: AutoHealLocator):
        """
        Initialize base page.
       
        Args:
            page: Playwright page instance.
            autoheal: AutoHeal locator instance.
        """
        self.page = page
        self.autoheal = autoheal
   
    async def navigate(self, url: str):
        """Navigate to URL."""
        await self.page.goto(url)
   
    async def get_title(self) -> str:
        """Get page title."""
        return await self.page.title()
   
    async def wait_for_load(self):
        """Wait for page to load."""
        await self.page.wait_for_load_state("networkidle")
