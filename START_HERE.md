# AutoHeal Playwright Python Demo — Start Here

This project demonstrates AI-powered self-healing test automation using the `autoheal-locator` Python package with Playwright.
Tests automatically fix broken element selectors when the UI changes — no manual selector maintenance needed.

---

## What This Project Does

Instead of writing a traditional Playwright selector that breaks when the UI changes:

```python
# Traditional — breaks if the selector changes
await page.locator("#user-name").fill("standard_user")
```

You write this:

```python
# AutoHeal — if the selector breaks, AI finds the element automatically
username = await autoheal_locator.find_element_async(
    "#user-name-BROKEN",
    "Username input field on the SauceDemo login page"
)
await username.fill("standard_user")
```

AutoHeal also works with native Playwright locators:

```python
# Native Playwright locator that's broken — AutoHeal fixes it too
username = await autoheal_locator.find_async(
    page.get_by_role("textbox", name="Username-BROKEN"),
    "Username input field on the SauceDemo login page"
)
```

When the selector fails, AutoHeal reads the page HTML, sends it to an AI, and returns the correct element.
The result is cached so AI is only called once per broken selector.

---

## Choose Your Path

| Goal | Time | What to do |
|------|------|------------|
| Just see it working | 5 min | Follow **Quick Demo** below |
| Understand the code | 15 min | Read the test files after running |
| Add it to your own project | 30 min | See **Using in Your Own Project** at the bottom |

---

## Quick Demo (5 minutes)

### Step 1 — Prerequisites

Make sure you have these installed:

- **Python 3.9+** — check with `python --version`
- **pip** — comes with Python

---

### Step 2 — Clone or Download the Project

```bash
git clone https://github.com/SanjayPG/playwright-autoheal-python-demo.git
cd playwright-autoheal-python-demo
```

Or download the ZIP from GitHub and extract it.

---

### Step 3 — Create a Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac / Linux
python -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` at the start of your terminal prompt.

---

### Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs `autoheal-locator[playwright]` from PyPI along with pytest and pytest-asyncio.

---

### Step 5 — Install Playwright Browsers

```bash
playwright install chromium
```

This downloads the Chromium browser that Playwright uses to run tests.
Only needs to be done once.

---

### Step 6 — Get a Free AI API Key

AutoHeal needs an AI provider to analyse pages and suggest selectors.
**Groq is completely free** and the fastest option to get started.

1. Go to **https://console.groq.com**
2. Sign up (free, no credit card)
3. Click **API Keys** → **Create API Key**
4. Copy the key (starts with `gsk_...`)

Other supported providers: OpenAI, Google Gemini, Anthropic, Ollama (local)

---

### Step 7 — Create and Configure Your .env File

The `.env` file is **not included in the repo** — it contains secret API keys and is listed in `.gitignore` so it will never be committed to GitHub.

You need to create it yourself. A template is already provided — copy it first:

```bash
# Windows
copy .env.example .env

# Mac / Linux
cp .env.example .env
```

Then open `.env` and add your key:

```bash
# Uncomment ONE of these blocks depending on your provider

# Groq (FREE — recommended for beginners)
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Google Gemini (also free tier available)
# GEMINI_API_KEY=your_key_here
# GEMINI_MODEL=gemini-2.0-flash

# OpenAI
# OPENAI_API_KEY=sk-your_key_here
# OPENAI_MODEL=gpt-4o-mini
```

Save the file. Only uncomment one provider at a time.

---

### Step 8 — Run the Demo Test

```bash
pytest tests/test_simple_heal.py -v -s
```

You will see AutoHeal healing broken selectors in real time:

```
[CONFIG] AI Provider: Groq
[CONFIG] Model: llama-3.3-70b-versatile
[CONFIG] Execution Strategy: SMART_SEQUENTIAL

tests/test_simple_heal.py::test_heal_broken_selector
[SUCCESS] [DOM] [1350ms] [820 tokens]  #user-name-BROKEN  ->  #user-name
Healed #user-name-BROKEN -> element found and filled successfully!
PASSED

tests/test_simple_heal.py::test_heal_broken_native_locator
[SUCCESS] [DOM] [1100ms] [790 tokens]  textbox[Username-BROKEN]  ->  #user-name
Healed native locator -> element found and filled successfully!
PASSED

tests/test_simple_heal.py::test_find_async_correct_locator
find_async() returned correct native locator without healing!
PASSED
```

---

### Step 9 — View the Reports

After the test run, reports are automatically generated in `autoheal-reports/`:

```
autoheal-reports/
├── AutoHeal_2026-02-13_AutoHeal_Report.html   ← Open this in a browser
├── AutoHeal_2026-02-13_AutoHeal_Report.json
└── AutoHeal_2026-02-13_AutoHeal_Report.txt
```

Open the HTML report in your browser for a full dashboard showing healing history,
cache hit rates, token usage and success rates.

---

## Running Other Tests

```bash
# Run all tests
pytest -v -s

# Run the simple healing demo (best starting point)
pytest tests/test_simple_heal.py -v -s

# Run SauceDemo login tests
pytest tests/test_login.py -v -s

# Run full SauceDemo test suite
pytest tests/test_saucedemo.py -v -s

# Run dynamic content tests
pytest tests/test_dynamic_content.py -v -s

# Run with debug logging to see full AI interaction
pytest tests/test_simple_heal.py -v -s --log-cli-level=DEBUG

# Run only healing-related tests (marked with @pytest.mark.healing)
pytest -m healing -v -s
```

---

## Project Structure

```
playwright-autoheal-python-demo/
├── tests/
│   ├── test_simple_heal.py         # Main demo — broken selectors healed by AI
│   ├── test_login.py               # Login test variations
│   ├── test_saucedemo.py           # Full SauceDemo test suite
│   ├── test_dynamic_content.py     # Dynamic/AJAX content tests
│   ├── test_autoheal_examples.py   # AutoHeal feature examples
│   └── test_all_locators.py        # All locator type demos
├── pages/
│   ├── base_page.py                # Base page class with AutoHeal
│   ├── login_page.py               # Login page object
│   ├── saucedemo_login_page.py     # SauceDemo login page
│   └── saucedemo_inventory_page.py # SauceDemo inventory page
├── config/
│   └── autoheal_config.py          # Builds AutoHeal config from .env
├── conftest.py                     # Pytest fixtures (browser + autoheal_locator)
├── requirements.txt                # Dependencies
├── pytest.ini                      # Pytest configuration
└── .env                            # Your API keys (never commit this)
```

---

## Playwright vs Selenium — Key Difference

AutoHeal works slightly differently with Playwright because Playwright uses async/await:

| | Selenium | Playwright |
|---|---|---|
| Find by string selector | `autoheal.find_element(selector, desc)` | `await autoheal_locator.find_element_async(selector, desc)` |
| Find by native locator | Not applicable | `await autoheal_locator.find_async(locator, desc)` |
| All methods | Synchronous | Async (requires `await`) |

---

## How AutoHeal Works (Simple Explanation)

```
Test uses broken selector  →  Playwright fails to find element
         │
         ▼
AutoHeal checks cache  →  Cache hit? Return cached selector immediately
         │
         ▼ (cache miss)
AutoHeal reads page HTML
         │
         ▼
Sends HTML + description to AI  →  "Find the element described as: Username input field"
         │
         ▼
AI returns working selector  →  "#user-name"
         │
         ▼
Playwright finds element  →  Test continues
         │
         ▼
Result saved to cache  →  Next run is instant (no AI call needed)
```

---

## Execution Strategies

Control how AutoHeal heals in `.env`:

```bash
AUTOHEAL_EXECUTION_STRATEGY=SMART_SEQUENTIAL
```

| Strategy | Description | Best For |
|----------|-------------|----------|
| `SMART_SEQUENTIAL` | DOM first, visual screenshot fallback | Most projects (default) |
| `DOM_ONLY` | DOM analysis only, no screenshots | CI/CD, cost-sensitive |
| `VISUAL_FIRST` | Screenshot first, DOM fallback | Visually complex UIs |
| `PARALLEL` | Both simultaneously, first result wins | Speed-critical scenarios |

---

## Supported AI Providers

| Provider | Free Tier | Visual Support | Setup |
|----------|-----------|---------------|-------|
| Groq | Yes (generous) | No (use DOM_ONLY) | `GROQ_API_KEY` |
| Google Gemini | Yes (limited) | Yes | `GEMINI_API_KEY` |
| OpenAI | No (paid) | Yes | `OPENAI_API_KEY` |
| Anthropic | No (paid) | Yes | `ANTHROPIC_API_KEY` |
| Ollama | Free (local) | Depends on model | `AUTOHEAL_API_URL` |

---

## Using AutoHeal in Your Own Playwright Project

### Install

```bash
pip install autoheal-locator[playwright]
```

### Basic Setup

```python
import pytest
from playwright.async_api import async_playwright
from autoheal.impl.adapter import PlaywrightWebAutomationAdapter
from autoheal.reporting.reporting_autoheal_locator import ReportingAutoHealLocator
from autoheal.config.ai_config import AIConfig, AIProvider
from autoheal.config.autoheal_config import AutoHealConfiguration

# Configure AI
ai_config = AIConfig.builder() \
    .provider(AIProvider.GROQ) \
    .api_key("gsk_your_key") \
    .model("llama-3.3-70b-versatile") \
    .build()

config = AutoHealConfiguration.builder().ai(ai_config).build()

# In your test or fixture:
async with async_playwright() as p:
    browser = await p.chromium.launch()
    page = await browser.new_page()

    adapter = PlaywrightWebAutomationAdapter(page)
    locator = ReportingAutoHealLocator(adapter, config)

    # Use instead of page.locator(...)
    element = await locator.find_element_async("#broken-selector", "Description of element")
    await element.fill("some value")
```

### pytest fixture pattern (recommended)

```python
@pytest.fixture
async def autoheal_locator(page):
    adapter = PlaywrightWebAutomationAdapter(page)
    locator = ReportingAutoHealLocator(adapter, config)
    yield locator
    locator.shutdown()  # generates reports
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'autoheal'`**
- Make sure your virtual environment is activated: `.venv\Scripts\activate`
- Run `pip install -r requirements.txt` again

**`ModuleNotFoundError: No module named 'playwright'`**
- Install with the playwright extra: `pip install autoheal-locator[playwright]`
- Then: `playwright install chromium`

**`No API key found`**
- Check your `.env` file has the key uncommented (no `#` at the start)
- Make sure there are no spaces around `=`: `GROQ_API_KEY=gsk_abc` not `GROQ_API_KEY = gsk_abc`

**`Browser not found` error**
- Run `playwright install chromium` — browsers must be installed separately

**Gemini 429 rate limit error**
- Free tier Gemini has low limits on visual calls
- Switch to `AUTOHEAL_EXECUTION_STRATEGY=DOM_ONLY` in `.env`

---

## Links

- **PyPI package**: https://pypi.org/project/autoheal-locator/
- **Library source**: https://github.com/SanjayPG/autoheal-locator-python
- **SauceDemo test site**: https://www.saucedemo.com
- **Playwright Python docs**: https://playwright.dev/python
- **Groq free API key**: https://console.groq.com
- **Google Gemini API key**: https://makersuite.google.com/app/apikey
