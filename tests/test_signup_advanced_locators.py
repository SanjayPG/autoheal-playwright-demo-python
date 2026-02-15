"""
Advanced locator tests for the Sign-up page.

Mirrors the JavaScript/TypeScript AutoHeal examples using:
  - get_by_role with duplicate buttons (second Submit)
  - get_by_role checkbox with wrong name (healing)
  - get_by_test_id with wrong ID (healing)
  - Shadow DOM element interaction
  - listitem filter
  - Chained filter with wrong button name (healing)

Each test uses an intentionally WRONG locator so AutoHeal can demonstrate
self-healing via AI.
"""

import pytest
from pathlib import Path
import asyncio



# Resolve the local HTML test fixture
FIXTURE_PATH = Path(__file__).parent / "fixtures" / "signup_page.html"
FIXTURE_URL = FIXTURE_PATH.as_uri()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _goto(page):
    """Navigate to the local sign-up page fixture."""
    await page.goto(FIXTURE_URL)
    await page.wait_for_load_state("domcontentloaded")


# ===================================================================
# 1. Submit button (second) — wrong description triggers healing
# ===================================================================

class TestSubmitButton:

    @pytest.mark.asyncio
    async def test_correct_second_submit_button(self, page, autoheal_locator):
        """Verify we can find the second Submit button with the correct locator."""

        autoheal_locator.clear_cache()
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_role("button", name="Submit"),
            "Second Submit button",
        )
        await loc.click()
        assert await loc.count() == 1
        assert await loc.text_content() == "Submit"

        await asyncio.sleep(5)

    @pytest.mark.healing
    @pytest.mark.asyncio
    async def test_heal_submit_button_wrong_name(self, page, autoheal_locator):
        """AutoHeal should fix a button role locator with wrong name."""
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_role("button", name="Submit Form"),  # Wrong name
            "Second Submit button on the sign-up page",
        )
        assert await loc.count() >= 1


# ===================================================================
# 2. Checkbox — wrong name triggers healing
# ===================================================================

class TestCheckbox:

    @pytest.mark.asyncio
    async def test_correct_subscribe_checkbox(self, page, autoheal_locator):
        """Verify the Subscribe checkbox with correct locator."""
        autoheal_locator.clear_cache()
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_role("checkbox", name="Subscribe Me"),
            "Subscribe checkbox",
        )
        assert await loc.count() == 1

    @pytest.mark.healing
    @pytest.mark.asyncio
    async def test_heal_checkbox_wrong_name(self, page, autoheal_locator):
        """AutoHeal should fix checkbox locator with wrong name 'Subscribe me'."""
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_role("checkbox", name="Subscribe me"),  # Wrong name
            "Subscribe checkbox on the sign-up form",
        )
        assert await loc.count() >= 1


# ===================================================================
# 3. get_by_test_id — wrong test ID triggers healing
# ===================================================================

class TestGetByTestId:

    @pytest.mark.asyncio
    async def test_correct_testid_directions(self, page, autoheal_locator):
        """Verify the Itinéraire button with correct test ID."""
        autoheal_locator.clear_cache()
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_test_id("directions123"),
            "Itinéraire button",
        )
        assert await loc.count() == 1

    @pytest.mark.healing
    @pytest.mark.asyncio
    async def test_heal_wrong_testid(self, page, autoheal_locator):
        """AutoHeal should fix a wrong test ID (directions123 -> directions)."""
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_test_id("directions123"),  # Wrong test ID
            "Itinéraire button",
        )
        assert await loc.count() >= 1


# ===================================================================
# 4. Shadow DOM — wrong role name triggers healing
# ===================================================================

class TestShadowDOM:

    @pytest.mark.asyncio
    async def test_correct_shadow_dom_details(self, page, autoheal_locator):
        """Verify the x-details element with role=button."""
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_role("button", name="Title123"),
            "Details button inside the shadow DOM",
        )
        assert await loc.count() == 1

    @pytest.mark.healing
    @pytest.mark.asyncio
    async def test_heal_shadow_dom_wrong_name(self, page, autoheal_locator):
        """AutoHeal should fix shadow DOM element with wrong button name."""
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_role("button", name="button"),  # Wrong name
            "Details button inside the shadow DOM",
        )
        assert await loc.count() >= 1


# ===================================================================
# 5. List item filter — filter by text
# ===================================================================

class TestListItemFilter:

    @pytest.mark.asyncio
    async def test_correct_listitem_filter(self, page, autoheal_locator):
        """Verify list item with 'Add to cart' text for Product 2."""
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_role("listitem").filter(has_text="Product 1234"),
            "Product 2 list item",
        )
        assert await loc.count() == 1
        await asyncio.sleep(15)

    @pytest.mark.healing
    @pytest.mark.asyncio
    async def test_heal_listitem_wrong_filter_text(self, page, autoheal_locator):
        """AutoHeal should fix list item filter with wrong text."""
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_role("listitem").filter(has_text="Add to cart"),  # Matches both products
            "Add to cart list item for Product 1",
        )
        assert await loc.count() >= 1


# ===================================================================
# 6. Chained filter — wrong button name triggers healing
# ===================================================================

class TestChainedFilter:

    @pytest.mark.asyncio
    async def test_correct_chained_filter(self, page, autoheal_locator):
        """Verify chained filter: list item with John + Say goodbye button."""
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_role("listitem")
                .filter(has_text="John")
                .filter(has=page.get_by_role("button", name="Say goodboye")),
            "List item containing John with Say goodbye button",
        )
        assert await loc.count() == 1

    @pytest.mark.healing
    @pytest.mark.asyncio
    async def test_heal_chained_filter_wrong_button_name(self, page, autoheal_locator):
        """AutoHeal should fix chained filter with wrong button name 'goodboy'."""
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_role("listitem")
                .filter(has_text="John")
                .filter(has=page.get_by_role("button", name="Say goodboy")),  # Wrong name
            "List item containing John with Say goodbye button",
        )
        assert await loc.count() >= 1


# ===================================================================
# 7. Additional locator types on the sign-up page
# ===================================================================

class TestAdditionalLocators:

    @pytest.mark.asyncio
    async def test_get_by_text_welcome(self, page, autoheal_locator):
        """Find the welcome message by text."""
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_text("Welcome, Johny"),
            "Welcome message for John",
        )
        assert await loc.count() == 1

    @pytest.mark.asyncio
    async def test_get_by_alt_text_logo(self, page, autoheal_locator):
        """Find the Playwright logo by alt text."""
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_alt_text("Playwright logon"),
            "Playwright logo image",
        )
        assert await loc.count() == 1

    @pytest.mark.asyncio
    async def test_get_by_title_issues(self, page, autoheal_locator):
        """Find the issues count by title attribute."""
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_title("Issues number"),
            "Issues count span",
        )
        assert await loc.count() == 1
        text = await loc.text_content()
        assert "25 issues" in text

    @pytest.mark.healing
    @pytest.mark.asyncio
    async def test_heal_wrong_alt_text(self, page, autoheal_locator):
        """AutoHeal should fix wrong alt text for the logo."""
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_alt_text("Playwright Logo Image"),  # Wrong alt text
            "Playwright logo image on the sign-up page",
        )
        assert await loc.count() >= 1

    @pytest.mark.healing
    @pytest.mark.asyncio
    async def test_heal_wrong_title(self, page, autoheal_locator):
        """AutoHeal should fix wrong title attribute."""
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_title("Issues Counter"),  # Wrong title
            "The span element with title='Issues count' showing 25 issues",
        )
        assert await loc.count() >= 1
