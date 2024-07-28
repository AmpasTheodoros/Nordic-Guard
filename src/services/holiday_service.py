# src/services/holiday_service.py

import pandas as pd
from src.utils.caching import cached_get_request
from src.utils.rate_limiter import RateLimiter
import streamlit as st

holiday_limiter = RateLimiter(calls=10, period=60)

def fetch_public_holidays(country_code: str) -> dict:
    holiday_limiter.wait()
    current_year = pd.Timestamp.now().year
    url = f"https://date.nager.at/api/v3/PublicHolidays/{current_year}/{country_code}"
    
    try:
        response = cached_get_request(url)
        response.raise_for_status()
        holidays = response.json()
        return {
            "country": country_code,
            "year": current_year,
            "holidays": [f"{h['date']} - {h['name']}" for h in holidays[:5]]
        }
    except Exception as e:
        st.error(f"Failed to fetch public holidays: {str(e)}")
        return {"error": "Failed to fetch public holidays"}