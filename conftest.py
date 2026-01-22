"""
Pytest configuration and fixtures for AutoHeal Playwright tests.
"""

import pytest
import asyncio
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

from autoheal import AutoHealLocator
from autoheal.impl.adapter import PlaywrightWebAutomationAdapter
from config.autoheal_config import get_autoheal_config


@pytest.fixture(scope="session")
def event_loop_policy():
    """Return the event loop policy."""
    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture(scope="function")
async def browser():
    """Launch browser for each test function."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,  # Set to False to see the browser
            slow_mo=100  # Reduce slowdown for faster tests
        )
        yield browser
        await browser.close()


@pytest.fixture(scope="function")
async def context(browser: Browser):
    """Create a new browser context for each test."""
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Playwright AutoHeal Demo)'
    )
    yield context
    await context.close()


@pytest.fixture(scope="function")
async def page(context: BrowserContext):
    """Create a new page for each test."""
    page = await context.new_page()
    yield page
    await page.close()


@pytest.fixture(scope="function")
def autoheal_locator(page: Page):
    """Create AutoHeal locator with Playwright adapter."""
    config = get_autoheal_config()
    adapter = PlaywrightWebAutomationAdapter(page)

    locator = AutoHealLocator.builder() \
        .with_web_adapter(adapter) \
        .with_configuration(config) \
        .build()

    yield locator

    # Print metrics after each test
    metrics = locator.get_metrics()
    cache_metrics = locator.get_cache_metrics()

    print("\n" + "="*60)
    print("AutoHeal Test Metrics:")
    print("="*60)
    print(f"Total requests: {metrics.total_requests}")
    print(f"Successful: {metrics.successful_requests}")
    print(f"Failed: {metrics.total_requests - metrics.successful_requests}")
    print(f"Success rate: {metrics.get_success_rate():.1%}")
    print(f"\nCache hits: {cache_metrics.total_hits}")
    print(f"Cache misses: {cache_metrics.total_misses}")
    print(f"Hit rate: {cache_metrics.get_hit_rate():.1%}")

    if cache_metrics.total_hits > 0:
        print(f"\nSaved {cache_metrics.total_hits} AI API calls!")
    print("="*60)


@pytest.fixture(autouse=True)
def print_test_info(request):
    """Print test information before each test."""
    print(f"\n{'='*60}")
    print(f"Running: {request.node.nodeid}")
    print(f"{'='*60}\n")
    yield
