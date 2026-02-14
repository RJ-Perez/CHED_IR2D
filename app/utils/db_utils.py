import functools
import time
import logging

_cache = {}
_cache_ttl = {}
DEFAULT_TTL = 300
_institutions_cache = None
_institutions_cache_time = 0
INSTITUTIONS_CACHE_TTL = 300
_reports_cache = None
_reports_cache_time = 0
REPORTS_CACHE_TTL = 120


def cached_query(key: str, ttl: int = DEFAULT_TTL):
    """Helper for caching query results."""

    def get_cached():
        if key in _cache and time.time() < _cache_ttl.get(key, 0):
            return _cache[key]
        return None

    def set_cached(value):
        _cache[key] = value
        _cache_ttl[key] = time.time() + ttl

    return (get_cached, set_cached)


def clear_cache(key: str = None):
    """Clear specific key or entire cache."""
    global _cache, _cache_ttl
    if key:
        _cache.pop(key, None)
        _cache_ttl.pop(key, None)
    else:
        _cache = {}
        _cache_ttl = {}


def get_cached_institutions():
    global _institutions_cache, _institutions_cache_time
    if _institutions_cache and time.time() < _institutions_cache_time:
        return _institutions_cache
    return None


def set_cached_institutions(data):
    global _institutions_cache, _institutions_cache_time
    _institutions_cache = data
    _institutions_cache_time = time.time() + INSTITUTIONS_CACHE_TTL


def get_cached_reports():
    global _reports_cache, _reports_cache_time
    if _reports_cache and time.time() < _reports_cache_time:
        return _reports_cache
    return None


def set_cached_reports(data):
    global _reports_cache, _reports_cache_time
    _reports_cache = data
    _reports_cache_time = time.time() + REPORTS_CACHE_TTL