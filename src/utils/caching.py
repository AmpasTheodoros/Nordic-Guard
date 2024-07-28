# src/utils/caching.py

from functools import lru_cache
import requests
import json

def hashable_cache(func):
    cache = {}

    def wrapper(*args, **kwargs):
        key = (json.dumps(args), json.dumps(kwargs, sort_keys=True))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper

@hashable_cache
def cached_get_request(url: str, headers: dict = None) -> requests.Response:
    return requests.get(url, headers=headers)

@lru_cache(maxsize=100)
def cached_post_request(url: str, payload: str) -> requests.Response:
    return requests.post(url, data=payload)
