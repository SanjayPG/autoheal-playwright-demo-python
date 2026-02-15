"""
Comprehensive tests for find_async() with ALL Playwright locator types.

Validates that AutoHeal can:
  1. Pass through correct native locators unchanged.
  2. Heal broken native locators via AI for every locator type.

Locator types tested:
  - get_by_role
  - get_by_text
  - get_by_label
  - get_by_placeholder
  - get_by_alt_text
  - get_by_title
  - get_by_test_id
  - locator (CSS selector)
  - locator (XPath)
"""

import os
import pytest
from pathlib import Path


# Resolve the local HTML test fixture
FIXTURE_PATH = Path(__file__).parent / "fixtures" / "locator_test_page.html"
FIXTURE_URL = FIXTURE_PATH.as_uri()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _goto(page):
    """Navigate to the local test fixture page."""
    await page.goto(FIXTURE_URL)
    await page.wait_for_load_state("domcontentloaded")


# ===================================================================
# 1.  get_by_role
# ===================================================================

class TestGetByRole:

    @pytest.mark.asyncio
    async def test_correct_button(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_role("button", name="Submit"),
            "Submit button",
        )
        assert await loc.count() == 1
        assert await loc.text_content() == "Submit"

    @pytest.mark.asyncio
    async def test_correct_checkbox(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_role("checkbox", name="I agree to the terms"),
            "Agree checkbox",
        )
        assert await loc.count() == 1

    @pytest.mark.asyncio
    async def test_correct_link(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_role("link", name="About Us"),
            "About Us navigation link",
        )
        assert await loc.count() == 1

    @pytest.mark.asyncio
    async def test_correct_heading(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_role("heading", name="Roles Section"),
            "Roles section heading",
        )
        assert await loc.count() == 1

    @pytest.mark.healing
    @pytest.mark.asyncio
    async def test_heal_wrong_button_name(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_role("button", name="Submit-WRONG"),
            "Submit button in the Roles Section",
        )
        assert await loc.count() >= 1


# ===================================================================
# 2.  get_by_text
# ===================================================================

class TestGetByText:

    @pytest.mark.asyncio
    async def test_correct_text(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_text("Welcome to the test page"),
            "Welcome paragraph",
        )
        assert await loc.count() == 1

    @pytest.mark.asyncio
    async def test_correct_text_partial(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_text("Status: Active"),
            "Status text span",
        )
        assert await loc.count() == 1

    @pytest.mark.healing
    @pytest.mark.asyncio
    async def test_heal_wrong_text(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_text("Operation completed WRONG"),
            "Success message div in the Text Section",
        )
        assert await loc.count() >= 1


# ===================================================================
# 3.  get_by_label
# ===================================================================

class TestGetByLabel:

    @pytest.mark.asyncio
    async def test_correct_label_username(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_label("Username"),
            "Username input field",
        )
        assert await loc.count() == 1
        await loc.fill("testuser")
        assert await loc.input_value() == "testuser"

    @pytest.mark.asyncio
    async def test_correct_label_password(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_label("Password"),
            "Password input field",
        )
        assert await loc.count() == 1

    @pytest.mark.asyncio
    async def test_correct_label_textarea(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_label("Biography"),
            "Biography textarea",
        )
        assert await loc.count() == 1
        await loc.fill("Hello world")
        assert await loc.input_value() == "Hello world"

    @pytest.mark.healing
    @pytest.mark.asyncio
    async def test_heal_wrong_label(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_label("Email-WRONG"),
            "Email Address input field in the Labels Section",
        )
        assert await loc.count() >= 1


# ===================================================================
# 4.  get_by_placeholder
# ===================================================================

class TestGetByPlaceholder:

    @pytest.mark.asyncio
    async def test_correct_placeholder_name(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_placeholder("Enter your name"),
            "Name input",
        )
        assert await loc.count() == 1
        await loc.fill("Alice")
        assert await loc.input_value() == "Alice"

    @pytest.mark.asyncio
    async def test_correct_placeholder_email(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_placeholder("name@example.com"),
            "Email input",
        )
        assert await loc.count() == 1

    @pytest.mark.asyncio
    async def test_correct_placeholder_search(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_placeholder("Search..."),
            "Search input",
        )
        assert await loc.count() == 1

    @pytest.mark.healing
    @pytest.mark.asyncio
    async def test_heal_wrong_placeholder(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_placeholder("Phone Number WRONG"),
            "Phone number input with placeholder (555) 123-4567 in the Placeholder Section",
        )
        assert await loc.count() >= 1


# ===================================================================
# 5.  get_by_alt_text
# ===================================================================

class TestGetByAltText:

    @pytest.mark.asyncio
    async def test_correct_alt_text(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_alt_text("Company Logo"),
            "Company logo image",
        )
        assert await loc.count() == 1

    @pytest.mark.asyncio
    async def test_correct_alt_text_avatar(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_alt_text("User Avatar"),
            "User avatar image",
        )
        assert await loc.count() == 1

    @pytest.mark.healing
    @pytest.mark.asyncio
    async def test_heal_wrong_alt_text(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_alt_text("Logo-WRONG"),
            "Company Logo image (alt text) in the Images Section",
        )
        assert await loc.count() >= 1


# ===================================================================
# 6.  get_by_title
# ===================================================================

class TestGetByTitle:

    @pytest.mark.asyncio
    async def test_correct_title(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_title("Total Issues"),
            "Issues count element",
        )
        assert await loc.count() == 1
        text = await loc.text_content()
        assert "42" in text

    @pytest.mark.asyncio
    async def test_correct_title_pr(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_title("Open Pull Requests"),
            "PR count element",
        )
        assert await loc.count() == 1

    @pytest.mark.healing
    @pytest.mark.asyncio
    async def test_heal_wrong_title(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_title("Help-WRONG"),
            "The anchor <a> element with title='Click for help' and text 'Need Help?' in the Title Section",
        )
        assert await loc.count() >= 1


# ===================================================================
# 7.  get_by_test_id
# ===================================================================

class TestGetByTestId:

    @pytest.mark.asyncio
    async def test_correct_testid_button(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_test_id("save-button"),
            "Save button",
        )
        assert await loc.count() == 1
        assert await loc.text_content() == "Save"

    @pytest.mark.asyncio
    async def test_correct_testid_input(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_test_id("search-field"),
            "Search field",
        )
        assert await loc.count() == 1
        await loc.fill("query")
        assert await loc.input_value() == "query"

    @pytest.mark.asyncio
    async def test_correct_testid_panel(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_test_id("results-panel"),
            "Results panel",
        )
        assert await loc.count() == 1

    @pytest.mark.healing
    @pytest.mark.asyncio
    async def test_heal_wrong_testid(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.get_by_test_id("delete-btn-WRONG"),
            "The <button> element with attribute data-testid='delete-button' and text 'Delete' in the Test ID Section",
        )
        assert await loc.count() >= 1


# ===================================================================
# 8.  CSS Selector via page.locator()
# ===================================================================

class TestCSSSelector:

    @pytest.mark.asyncio
    async def test_correct_css_id(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.locator("#first-card"),
            "First card div",
        )
        assert await loc.count() == 1

    @pytest.mark.asyncio
    async def test_correct_css_class(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.locator("#first-card .card-title"),
            "First card title",
        )
        assert await loc.count() == 1
        assert await loc.text_content() == "First Card"

    @pytest.mark.healing
    @pytest.mark.asyncio
    async def test_heal_wrong_css(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.locator("#second-card-WRONG .card-title"),
            "Second Card title paragraph inside div#second-card in the CSS and XPath Section",
        )
        assert await loc.count() >= 1


# ===================================================================
# 9.  XPath via page.locator()
# ===================================================================

class TestXPath:

    @pytest.mark.asyncio
    async def test_correct_xpath(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.locator("//div[@id='second-card']//p[@class='card-body']"),
            "Second card body paragraph",
        )
        assert await loc.count() == 1
        text = await loc.text_content()
        assert "second card" in text.lower()

    @pytest.mark.healing
    @pytest.mark.asyncio
    async def test_heal_wrong_xpath(self, page, autoheal_locator):
        await _goto(page)
        loc = await autoheal_locator.find_async(
            page.locator("//div[@id='first-card-WRONG']//p[@class='card-body']"),
            "The <p class='card-body'> paragraph with text 'Content of the first card.' inside div#first-card",
        )
        assert await loc.count() >= 1
