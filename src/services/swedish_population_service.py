# src/services/swedish_population_service.py

import json
from src.utils.caching import cached_post_request
from src.utils.rate_limiter import RateLimiter
import streamlit as st

scb_limiter = RateLimiter(calls=5, period=60)

def fetch_swedish_population_data() -> dict:
    scb_limiter.wait()
    url = "https://api.scb.se/OV0104/v1/doris/en/ssd/START/BE/BE0101/BE0101A/BefolkningNy"
    payload = {
        "query": [
            {
                "code": "Tid",
                "selection": {
                    "filter": "item",
                    "values": [
                        "2023"
                    ]
                }
            }
        ],
        "response": {"format": "json"}
    }
    try:
        response = cached_post_request(url, json.dumps(payload))
        response.raise_for_status()
        data = response.json()
        return {"total_population": data["data"][0]["values"][0]}
    except Exception as e:
        st.error(f"Failed to fetch population data: {str(e)}")
        return {"error": "Failed to fetch population data"}