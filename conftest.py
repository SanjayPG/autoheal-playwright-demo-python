"""
Pytest configuration and fixtures for AutoHeal Playwright tests.

Browser and test settings are driven by environment variables.
See .env.example for all available options.

Supports both sequential and parallel (pytest-xdist) test execution.
"""

import os
import json
import logging
import tempfile
from pathlib import Path
from datetime import datetime

import pytest
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

from autoheal.impl.adapter import PlaywrightWebAutomationAdapter
from autoheal.reporting import ReportingAutoHealLocator
from config.autoheal_config import get_autoheal_config

load_dotenv()

# Configure debug logging if AUTOHEAL_DEBUG is set
if os.getenv("AUTOHEAL_DEBUG", "").lower() in ("true", "1", "yes", "on"):
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(name)s - %(levelname)s - %(message)s"
    )
    logging.getLogger("autoheal").setLevel(logging.DEBUG)


# Directory for xdist worker report files
XDIST_REPORT_DIR = Path(tempfile.gettempdir()) / "autoheal_xdist_reports"


def is_xdist_worker(config):
    """Check if running as an xdist worker."""
    return hasattr(config, 'workerinput')


def is_xdist_controller(config):
    """Check if running as xdist controller (master) with workers.

    Returns True only if xdist is actively being used with -n option,
    not just if the plugin is installed.
    """
    if not config.pluginmanager.hasplugin('xdist'):
        return False
    if is_xdist_worker(config):
        return False
    # Check if xdist is actually being used (numprocesses > 0)
    numprocesses = getattr(config.option, 'numprocesses', None)
    return numprocesses is not None and numprocesses != 0


@pytest.fixture(scope="session")
def event_loop_policy():
    """Return the event loop policy."""
    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture(scope="session", autouse=True)
def setup_autoheal_reporting(request):
    """Setup AutoHeal reporting for the session."""
    # For sequential runs or xdist workers, collect reporters in memory
    request.config._autoheal_reporters = []

    # For xdist, ensure report directory exists
    if is_xdist_worker(request.config):
        XDIST_REPORT_DIR.mkdir(exist_ok=True)

    yield


@pytest.fixture(scope="function")
async def browser():
    """Launch browser for each test function."""
    headless_val = os.getenv("BROWSER_HEADLESS", "true")
    headless = headless_val.lower() not in ("false", "0", "no", "off")
    slow_mo = int(os.getenv("BROWSER_SLOW_MO", "100"))

    async with async_playwright() as p:
        p.selectors.set_test_id_attribute("data-test")
        browser = await p.chromium.launch(
            headless=headless,
            slow_mo=slow_mo,
        )
        yield browser
        await browser.close()


@pytest.fixture(scope="function")
async def context(browser: Browser):
    """Create a new browser context for each test."""
    viewport_width = int(os.getenv("BROWSER_VIEWPORT_WIDTH", "1920"))
    viewport_height = int(os.getenv("BROWSER_VIEWPORT_HEIGHT", "1080"))

    context = await browser.new_context(
        viewport={'width': viewport_width, 'height': viewport_height},
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
def autoheal_locator(page: Page, request):
    """Create AutoHeal locator with reporting for each test."""
    config = get_autoheal_config()
    adapter = PlaywrightWebAutomationAdapter(page)
    locator = ReportingAutoHealLocator(adapter, config)

    # Collect reporter for merging later
    if hasattr(request.config, '_autoheal_reporters'):
        request.config._autoheal_reporters.append(locator.reporter)

    yield locator

    # Print metrics
    metrics = locator.autoheal.get_metrics()
    cache_metrics = locator.autoheal.get_cache_metrics()
    print(f"\nAutoHeal: {metrics.successful_requests}/{metrics.total_requests} successful")
    print(f"Cache: {cache_metrics.total_hits} hits, {cache_metrics.total_misses} misses")


@pytest.fixture(autouse=True)
def print_test_info(request):
    """Print test information before each test."""
    print(f"\n{'='*60}")
    print(f"Running: {request.node.nodeid}")
    print(f"{'='*60}\n")
    yield


def pytest_configure(config):
    """Called after command line options have been parsed."""
    # Clean up old xdist report files at start
    if not is_xdist_worker(config):
        if XDIST_REPORT_DIR.exists():
            for f in XDIST_REPORT_DIR.glob("worker_*.json"):
                try:
                    f.unlink()
                except:
                    pass


def pytest_sessionfinish(session, exitstatus):
    """Generate AutoHeal reports at the end of test session."""
    config = session.config
    reporters = getattr(config, '_autoheal_reporters', [])

    if is_xdist_worker(config):
        # Worker: Save reports to file for master to collect
        if reporters:
            worker_id = config.workerinput.get('workerid', 'unknown')
            try:
                XDIST_REPORT_DIR.mkdir(parents=True, exist_ok=True)

                # Serialize reports to JSON
                all_reports = []
                for reporter in reporters:
                    for report in reporter.reports:
                        all_reports.append({
                            'original_selector': report.original_selector,
                            'actual_selector': report.actual_selector,
                            'strategy': str(report.strategy),
                            'execution_time_ms': report.execution_time_ms,
                            'success': report.success,
                            'element_details': report.element_details,
                            'reasoning': report.reasoning,
                            'description': report.description,
                            'timestamp': report.timestamp.isoformat() if report.timestamp else None,
                            'tokens_used': report.tokens_used,
                        })

                report_file = XDIST_REPORT_DIR / f"worker_{worker_id}.json"
                with open(report_file, 'w') as f:
                    json.dump(all_reports, f)
            except Exception as e:
                pass  # Silently fail - reports are best-effort

    elif is_xdist_controller(config):
        # Controller: Collect and merge worker reports
        _generate_merged_xdist_reports()

    else:
        # Sequential run: Generate reports directly
        if reporters:
            _generate_reports_from_reporters(reporters)


def _generate_reports_from_reporters(reporters):
    """Generate reports from collected reporters."""
    print("\n" + "=" * 60)
    print("GENERATING AUTOHEAL REPORTS")
    print("=" * 60)

    output_dir = Path(__file__).parent / "autoheal-reports"
    output_dir.mkdir(exist_ok=True)

    # Merge all reports into the first reporter
    main_reporter = reporters[0]
    for reporter in reporters[1:]:
        main_reporter.reports.extend(reporter.reports)

    # Generate reports
    original_cwd = os.getcwd()
    try:
        os.chdir(output_dir)
        main_reporter.generate_html_report()
        main_reporter.generate_json_report()
        main_reporter.generate_text_report()
        main_reporter.print_summary()
    finally:
        os.chdir(original_cwd)


def _generate_merged_xdist_reports():
    """Merge reports from all xdist workers and generate final report."""
    from autoheal.reporting import AutoHealReporter, SelectorReport, SelectorStrategy
    from config.autoheal_config import get_autoheal_config

    if not XDIST_REPORT_DIR.exists():
        return

    worker_files = list(XDIST_REPORT_DIR.glob("worker_*.json"))
    if not worker_files:
        return

    print("\n" + "=" * 60)
    print("GENERATING AUTOHEAL REPORTS (merged from parallel workers)")
    print("=" * 60)

    # Load all worker reports
    all_reports = []
    for wf in worker_files:
        try:
            with open(wf, 'r') as f:
                all_reports.extend(json.load(f))
        except:
            pass

    if not all_reports:
        return

    # Create a reporter and add all reports
    config = get_autoheal_config()
    ai_config = getattr(config, 'ai_config', None)
    reporter = AutoHealReporter(ai_config)

    # Convert JSON back to SelectorReport objects
    strategy_map = {
        'SelectorStrategy.ORIGINAL_SELECTOR': SelectorStrategy.ORIGINAL_SELECTOR,
        'SelectorStrategy.CACHED': SelectorStrategy.CACHED,
        'SelectorStrategy.DOM_ANALYSIS': SelectorStrategy.DOM_ANALYSIS,
        'SelectorStrategy.VISUAL_ANALYSIS': SelectorStrategy.VISUAL_ANALYSIS,
        'SelectorStrategy.AI_DISAMBIGUATION': SelectorStrategy.AI_DISAMBIGUATION,
        'SelectorStrategy.FAILED': SelectorStrategy.FAILED,
    }

    for r in all_reports:
        strategy = strategy_map.get(r['strategy'], SelectorStrategy.DOM_ANALYSIS)
        timestamp = datetime.fromisoformat(r['timestamp']) if r['timestamp'] else datetime.now()

        report = SelectorReport(
            original_selector=r['original_selector'],
            actual_selector=r['actual_selector'],
            description=r['description'],
            strategy=strategy,
            execution_time_ms=r['execution_time_ms'],
            success=r['success'],
            element_details=r['element_details'],
            reasoning=r['reasoning'],
            tokens_used=r['tokens_used'],
            timestamp=timestamp,
        )
        reporter.reports.append(report)

    # Generate reports
    output_dir = Path(__file__).parent / "autoheal-reports"
    output_dir.mkdir(exist_ok=True)

    original_cwd = os.getcwd()
    try:
        os.chdir(output_dir)
        reporter.generate_html_report()
        reporter.generate_json_report()
        reporter.generate_text_report()
        reporter.print_summary()
    finally:
        os.chdir(original_cwd)

    # Cleanup worker files
    for wf in worker_files:
        try:
            wf.unlink()
        except:
            pass
