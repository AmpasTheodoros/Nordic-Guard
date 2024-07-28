# src/services/joke_service.py

from src.utils.caching import cached_get_request
from src.utils.rate_limiter import RateLimiter
import streamlit as st

joke_limiter = RateLimiter(calls=5, period=60)

def fetch_random_joke() -> dict:
    joke_limiter.wait()
    url = "https://official-joke-api.appspot.com/random_joke"
    try:
        response = cached_get_request(url)
        response.raise_for_status()
        joke = response.json()
        return {"setup": joke['setup'], "punchline": joke['punchline']}
    except Exception as e:
        st.error(f"Failed to fetch joke: {str(e)}")
        return {"error": "Failed to fetch joke"}