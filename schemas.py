"""
Canonical job schema for Allseeing.
All company extractors must return job dicts that conform to this schema.
"""

from typing import Any

# Required fields every job must have (jobId must be string)
REQUIRED_KEYS = ("jobId", "title", "url", "detected")

# Recommended optional fields for dashboard/filtering
OPTIONAL_KEYS = ("company", "location", "posted_date", "updated_time", "source")


def ensure_job(source: str, job: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize a job dict to the canonical schema.
    - Sets "source" to the company identifier (e.g. "amazon", "meta").
    - Ensures "jobId" is a string.
    - Returns a new dict with at least required keys; preserves any optional keys.
    """
    out = dict(job)
    out["source"] = source
    if "jobId" in out and not isinstance(out["jobId"], str):
        out["jobId"] = str(out["jobId"])
    return out


def validate_job(job: dict[str, Any]) -> bool:
    """Return True if job has all required keys and types are acceptable."""
    if not isinstance(job, dict):
        return False
    for key in REQUIRED_KEYS:
        if key not in job or job[key] is None:
            return False
    if not isinstance(job.get("jobId"), str):
        return False
    if not isinstance(job.get("detected"), str):
        return False
    return True
