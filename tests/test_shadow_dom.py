"""
Test shadow DOM extraction functionality.
"""

import pytest
from playwright.async_api import async_playwright


@pytest.mark.asyncio
async def test_shadow_dom_extraction():
    """Test that shadow DOM content is extracted from page source."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Create a page with shadow DOM - use unique identifiers not in script
        await page.set_content("""
        <!DOCTYPE html>
        <html>
        <head><title>Shadow DOM Test</title></head>
        <body>
            <h1>Light DOM Title</h1>
            <div id="host">Host element</div>
            <script>
                // Create shadow DOM
                const host = document.getElementById('host');
                const shadow = host.attachShadow({ mode: 'open' });
                shadow.innerHTML = '<button id="btn-inside-shadow">Click Me In Shadow</button><p class="shadow-para">Paragraph Inside Shadow Root</p>';
            </script>
        </body>
        </html>
        """)

        # Wait for shadow DOM to be created
        await page.wait_for_timeout(100)

        # Import adapter and test shadow DOM extraction
        from autoheal.impl.adapter.playwright_adapter import PlaywrightWebAutomationAdapter
        adapter = PlaywrightWebAutomationAdapter(page)

        # Get page source with shadow DOM
        source_with_shadow = await adapter.get_page_source(include_shadow_dom=True)

        # Get regular page source (without shadow DOM)
        source_without_shadow = await adapter.get_page_source(include_shadow_dom=False)

        # The key test: shadow-root markers should only appear in the shadow-extracted version
        assert "<!-- shadow-root" in source_with_shadow, "Shadow root marker should be present"
        assert "<!-- /shadow-root -->" in source_with_shadow, "Shadow root closing marker should be present"

        # Regular page source should NOT have shadow-root markers
        assert "<!-- shadow-root" not in source_without_shadow, "Shadow root marker should NOT be in regular source"

        # Both should include the script tag content (which is light DOM)
        assert "btn-inside-shadow" in source_with_shadow
        assert "btn-inside-shadow" in source_without_shadow  # It's in the script text

        # Both should include light DOM
        assert "Light DOM Title" in source_with_shadow
        assert "Light DOM Title" in source_without_shadow

        print(f"\nSource WITH shadow DOM (length: {len(source_with_shadow)})")
        print(f"Source WITHOUT shadow DOM (length: {len(source_without_shadow)})")
        print("\nShadow DOM section found:")
        if "<!-- shadow-root" in source_with_shadow:
            start = source_with_shadow.find("<!-- shadow-root")
            end = source_with_shadow.find("<!-- /shadow-root -->") + 21
            print(source_with_shadow[start:end])

        await browser.close()


@pytest.mark.asyncio
async def test_shadow_dom_fallback_on_error():
    """Test that extraction falls back gracefully on error."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Simple page without shadow DOM
        await page.set_content("<html><body><p>Simple page</p></body></html>")

        from autoheal.impl.adapter.playwright_adapter import PlaywrightWebAutomationAdapter
        adapter = PlaywrightWebAutomationAdapter(page)

        # Should work without errors even on simple pages
        source = await adapter.get_page_source(include_shadow_dom=True)
        assert "Simple page" in source

        await browser.close()
