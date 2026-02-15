"""Page Object Model for AutoHeal Playwright demo."""

from .base_page import BasePage
from .login_page import LoginPage
from .saucedemo_login_page import SauceDemoLoginPage
from .saucedemo_inventory_page import SauceDemoInventoryPage

__all__ = [
    "BasePage",
    "LoginPage",
    "SauceDemoLoginPage",
    "SauceDemoInventoryPage",
]
