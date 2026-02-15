"""
SauceDemo Inventory Page Object.
Demonstrates AutoHeal for product catalog interactions.
"""

from playwright.async_api import Page
from autoheal import AutoHealLocator
from pages.base_page import BasePage


class SauceDemoInventoryPage(BasePage):
    """Inventory/Products page for saucedemo.com with self-healing selectors."""

    # Page title selector
    PAGE_TITLE = ".title"

    # Cart selectors
    SHOPPING_CART_LINK = ".shopping_cart_link"
    SHOPPING_CART_BADGE = ".shopping_cart_badge"

    # Product selectors
    INVENTORY_ITEM = ".inventory_item"
    INVENTORY_ITEM_NAME = ".inventory_item_name"
    INVENTORY_ITEM_PRICE = ".inventory_item_price"

    # Sort dropdown
    SORT_DROPDOWN = "[data-test='product-sort-container']"

    async def get_page_title(self):
        """Get the Products page title element."""
        return await self.autoheal.find_element_async(
            self.PAGE_TITLE,
            "Products page title"
        )

    async def get_page_title_text(self) -> str:
        """Get the Products page title text."""
        title_elem = await self.get_page_title()
        return await title_elem.text_content()

    async def add_product_to_cart(self, product_name: str):
        """
        Add a product to cart by name.

        Args:
            product_name: Product identifier for data-test attribute.
                         Examples: 'sauce-labs-backpack', 'sauce-labs-bike-light'
        """
        add_button = await self.autoheal.find_element_async(
            f"[data-test='add-to-cart-{product_name}']",
            f"Add to cart button for {product_name}"
        )
        await add_button.click()

    async def remove_product_from_cart(self, product_name: str):
        """
        Remove a product from cart by name.

        Args:
            product_name: Product identifier for data-test attribute.
        """
        remove_button = await self.autoheal.find_element_async(
            f"[data-test='remove-{product_name}']",
            f"Remove from cart button for {product_name}"
        )
        await remove_button.click()

    async def get_cart_item_count(self) -> int:
        """Get the number of items in cart from badge."""
        is_present = await self.autoheal.is_element_present_async(
            self.SHOPPING_CART_BADGE,
            "Shopping cart badge"
        )
        if not is_present:
            return 0

        cart_badge = await self.autoheal.find_element_async(
            self.SHOPPING_CART_BADGE,
            "Shopping cart badge"
        )
        text = (await cart_badge.text_content() or "").strip()
        return int(text) if text.isdigit() else 0

    async def go_to_cart(self):
        """Click on shopping cart to go to cart page."""
        cart_link = await self.autoheal.find_element_async(
            self.SHOPPING_CART_LINK,
            "Shopping cart link"
        )
        await cart_link.click()

    async def get_all_product_names(self) -> list:
        """Get list of all product names on the page."""
        elements = await self.autoheal.find_elements_async(
            self.INVENTORY_ITEM_NAME,
            "Inventory item names"
        )
        names = []
        for elem in elements:
            name = await elem.text_content()
            if name:
                names.append(name)
        return names

    async def get_product_price(self, product_name: str) -> str:
        """
        Get price of a specific product.

        Args:
            product_name: The visible name of the product.
        """
        # Find the product item container that has this name
        price_elem = await self.autoheal.find_element_async(
            f".inventory_item:has-text('{product_name}') .inventory_item_price",
            f"Price for {product_name}"
        )
        return await price_elem.text_content()

    async def select_sort_option(self, option_value: str):
        """
        Select a sorting option.

        Args:
            option_value: Value of the sort option.
                         Options: 'az', 'za', 'lohi', 'hilo'
        """
        sort_dropdown = await self.autoheal.find_element_async(
            self.SORT_DROPDOWN,
            "Product sort dropdown"
        )
        await sort_dropdown.select_option(option_value)
