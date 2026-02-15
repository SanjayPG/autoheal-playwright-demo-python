"""
Dynamic content tests demonstrating AutoHeal with async elements.
"""

import pytest
from playwright.async_api import Page
from autoheal import AutoHealLocator


@pytest.mark.dynamic
@pytest.mark.asyncio
async def test_dynamic_loading(page: Page, autoheal_locator: AutoHealLocator):
    """Test AutoHeal with dynamically loaded content."""
   
    await page.goto("https://the-internet.herokuapp.com/dynamic_loading/1")
   
    # Click start button
    start_btn = await autoheal_locator.find_element_async(
        "#start button",
        "Start button for dynamic loading"
    )
    await start_btn.click()
   
    # AutoHeal will wait and find the dynamically loaded element
    finish_text = await autoheal_locator.find_element_async(
        "#finish",
        "Finish message after loading completes"
    )
   
    text = await finish_text.text_content()
    assert "Hello World!" in text


@pytest.mark.dynamic
@pytest.mark.asyncio
async def test_dynamic_controls(page: Page, autoheal_locator: AutoHealLocator):
    """Test AutoHeal with dynamically added/removed elements."""
   
    await page.goto("https://the-internet.herokuapp.com/dynamic_controls")
   
    # Remove checkbox
    remove_btn = await autoheal_locator.find_element_async(
        "button",
        "Remove button for checkbox"
    )
    await remove_btn.click()
   
    # Wait for removal message
    await page.wait_for_selector("#message", state="visible")
   
    # Verify it's gone
    is_present = await autoheal_locator.is_element_present_async(
        "#checkbox input",
        "Checkbox element"
    )
    assert not is_present, "Checkbox should be removed"
