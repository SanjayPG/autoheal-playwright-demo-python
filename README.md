# AutoHeal Playwright Python Demo

A demo project showing AI-powered self-healing Playwright tests using the [`autoheal-locator`](https://pypi.org/project/autoheal-locator/) Python package.

When a selector breaks, AutoHeal automatically finds the correct element using AI — no manual fixes needed.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Playwright browser
playwright install chromium

# 3. Add your free Groq API key to .env
GROQ_API_KEY=gsk_your_key_here

# 4. Run the demo
pytest tests/test_simple_heal.py -v -s
```

See **[START_HERE.md](START_HERE.md)** for the full step-by-step guide.

## What You'll See

```
[SUCCESS] [DOM] [1350ms]  #user-name-BROKEN  ->  #user-name
[SUCCESS] [DOM] [1100ms]  textbox[Username-BROKEN]  ->  #user-name

Total: 3 | Success: 3 | Failed: 0 | DOM Healed: 2
```

## Install the Library

```bash
# Playwright support requires the [playwright] extra
pip install autoheal-locator[playwright]
```

## Links

- [START_HERE.md](START_HERE.md) — Full setup guide
- [PyPI](https://pypi.org/project/autoheal-locator/) — `pip install autoheal-locator[playwright]`
- [Library Source](https://github.com/SanjayPG/autoheal-locator-python) — GitHub
- [SauceDemo](https://www.saucedemo.com) — Test site used in this demo
- [Free Groq API Key](https://console.groq.com) — Get started for free
- [Playwright Python](https://playwright.dev/python) — Playwright docs
