"""AutoHeal configuration for Playwright tests."""

import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from autoheal import AutoHealConfiguration
from autoheal.config import (
    AIConfig,
    CacheConfig,
    CacheType,
    PerformanceConfig,
    ResilienceConfig,
    ReportingConfig,
)
from autoheal.models.enums import AIProvider, ExecutionStrategy


_PROVIDER_MAP = {
    "GROQ":             AIProvider.GROQ,
    "OPENAI":           AIProvider.OPENAI,
    "GOOGLE_GEMINI":    AIProvider.GOOGLE_GEMINI,
    "ANTHROPIC_CLAUDE": AIProvider.ANTHROPIC_CLAUDE,
    "DEEPSEEK":         AIProvider.DEEPSEEK,
    "GROK":             AIProvider.GROK,
    "LOCAL_MODEL":      AIProvider.LOCAL_MODEL,
}

_CACHE_TYPE_MAP = {
    "CAFFEINE":        CacheType.CAFFEINE,
    "PERSISTENT_FILE": CacheType.PERSISTENT_FILE,
    "REDIS":           CacheType.REDIS,
    "HYBRID":          CacheType.HYBRID,
}

_EXECUTION_STRATEGY_MAP = {
    "SMART_SEQUENTIAL": ExecutionStrategy.SMART_SEQUENTIAL,
    "SEQUENTIAL":        ExecutionStrategy.SEQUENTIAL,
    "PARALLEL":          ExecutionStrategy.PARALLEL,
    "DOM_ONLY":          ExecutionStrategy.DOM_ONLY,
    "VISUAL_FIRST":      ExecutionStrategy.VISUAL_FIRST,
}


def _get_bool(key: str, default: bool) -> bool:
    val = os.getenv(key)
    if val is None:
        return default
    return val.lower() not in ("false", "0", "no", "off")


def _get_int(key: str, default: int) -> int:
    val = os.getenv(key)
    return int(val) if val else default


def _get_float(key: str, default: float) -> float:
    val = os.getenv(key)
    return float(val) if val else default


def get_autoheal_config() -> AutoHealConfiguration:
    """Build AutoHeal configuration from environment variables."""

    # --- AI Config ---
    provider_name = os.getenv("AUTOHEAL_AI_PROVIDER", "GROQ").upper()
    provider = _PROVIDER_MAP.get(provider_name, AIProvider.GROQ)

    ai_config = AIConfig.builder() \
        .provider(provider) \
        .timeout(timedelta(milliseconds=_get_int("AUTOHEAL_AI_TIMEOUT", 30000))) \
        .max_retries(_get_int("AUTOHEAL_AI_MAX_RETRIES", 3)) \
        .visual_analysis_enabled(_get_bool("AUTOHEAL_AI_VISUAL_ANALYSIS_ENABLED", True)) \
        .temperature_dom(_get_float("AUTOHEAL_AI_TEMPERATURE_DOM", 0.1)) \
        .max_tokens_dom(_get_int("AUTOHEAL_AI_MAX_TOKENS_DOM", 2000)) \
        .build()

    # --- Cache Config ---
    cache_type_name = os.getenv("AUTOHEAL_CACHE_TYPE", "CAFFEINE").upper()
    cache_type = _CACHE_TYPE_MAP.get(cache_type_name, CacheType.CAFFEINE)

    cache_config = CacheConfig.builder() \
        .cache_type(cache_type) \
        .maximum_size(_get_int("AUTOHEAL_CACHE_MAXIMUM_SIZE", 10000)) \
        .expire_after_write(timedelta(milliseconds=_get_int("AUTOHEAL_CACHE_EXPIRE_AFTER_WRITE_MS", 86400000))) \
        .expire_after_access(timedelta(milliseconds=_get_int("AUTOHEAL_CACHE_EXPIRE_AFTER_ACCESS_MS", 7200000))) \
        .record_stats(_get_bool("AUTOHEAL_CACHE_RECORD_STATS", True)) \
        .build()

    # --- Performance Config ---
    strategy_name = os.getenv("AUTOHEAL_PERFORMANCE_EXECUTION_STRATEGY", "SMART_SEQUENTIAL").upper()
    execution_strategy = _EXECUTION_STRATEGY_MAP.get(strategy_name, ExecutionStrategy.SMART_SEQUENTIAL)

    performance_config = PerformanceConfig.builder() \
        .thread_pool_size(_get_int("AUTOHEAL_PERFORMANCE_THREAD_POOL_SIZE", 4)) \
        .element_timeout(timedelta(milliseconds=_get_int("AUTOHEAL_PERFORMANCE_ELEMENT_TIMEOUT_MS", 45000))) \
        .enable_metrics(_get_bool("AUTOHEAL_PERFORMANCE_ENABLE_METRICS", True)) \
        .execution_strategy(execution_strategy) \
        .build()

    # --- Resilience Config ---
    resilience_config = ResilienceConfig.builder() \
        .retry_max_attempts(_get_int("AUTOHEAL_RESILIENCE_RETRY_MAX_ATTEMPTS", 3)) \
        .retry_delay(timedelta(milliseconds=_get_int("AUTOHEAL_RESILIENCE_RETRY_DELAY_MS", 1000))) \
        .circuit_breaker_failure_threshold(_get_int("AUTOHEAL_RESILIENCE_CIRCUIT_BREAKER_THRESHOLD", 5)) \
        .circuit_breaker_timeout(timedelta(milliseconds=_get_int("AUTOHEAL_RESILIENCE_CIRCUIT_BREAKER_TIMEOUT_MS", 300000))) \
        .build()

    # --- Reporting Config ---
    output_dir = os.getenv(
        "AUTOHEAL_REPORTING_OUTPUT_DIRECTORY",
        str(Path(__file__).parent.parent / "autoheal-reports")
    )

    reporting_config = ReportingConfig.builder() \
        .enabled(_get_bool("AUTOHEAL_REPORTING_ENABLED", True)) \
        .generate_html(_get_bool("AUTOHEAL_REPORTING_GENERATE_HTML", True)) \
        .generate_json(_get_bool("AUTOHEAL_REPORTING_GENERATE_JSON", True)) \
        .console_logging(_get_bool("AUTOHEAL_REPORTING_CONSOLE_LOGGING", True)) \
        .output_directory(output_dir) \
        .build()

    return AutoHealConfiguration.builder() \
        .ai(ai_config) \
        .cache(cache_config) \
        .performance(performance_config) \
        .resilience(resilience_config) \
        .reporting(reporting_config) \
        .build()
