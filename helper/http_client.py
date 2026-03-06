"""
Shared HTTP client with timeout for aiohttp requests.
Companies can use this for consistent timeout behavior on HTTP calls.
"""

import aiohttp

# 60 second total timeout per request
DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=60, connect=10)


def session_with_timeout(timeout=None):
    """Return an aiohttp.ClientSession with sensible defaults."""
    return aiohttp.ClientSession(timeout=timeout or DEFAULT_TIMEOUT)
