"""
Run company extractors with timeout, retries, and error isolation.
"""

import asyncio
import time


async def run_extractor(extractor_fn, timeout_sec=60, max_retries=3):
    """
    Run an extractor with timeout and retries.
    Returns (result, duration_ms) on success, or (None, duration_ms, error) on failure.
    """
    last_error = None
    for attempt in range(max_retries):
        start = time.perf_counter()
        try:
            result = await asyncio.wait_for(extractor_fn(), timeout=timeout_sec)
            duration_ms = (time.perf_counter() - start) * 1000
            return (result, duration_ms)
        except asyncio.TimeoutError as e:
            last_error = e
            duration_ms = (time.perf_counter() - start) * 1000
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                return (None, duration_ms, last_error)
        except Exception as e:
            last_error = e
            duration_ms = (time.perf_counter() - start) * 1000
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                return (None, duration_ms, last_error)
    return (None, 0, last_error)
