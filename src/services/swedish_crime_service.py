# src/services/swedish_crime_service.py

from bs4 import BeautifulSoup
from src.utils.caching import cached_get_request
from src.utils.rate_limiter import RateLimiter
import streamlit as st

bra_limiter = RateLimiter(calls=3, period=60)

def fetch_swedish_crime_stats() -> dict:
    bra_limiter.wait()
    url = "https://bra.se/statistik/kriminalstatistik/anmalda-brott.html"
    try:
        response = cached_get_request(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        stats_div = soup.find('div', class_='statistics-summary')
        if stats_div:
            total_crimes = stats_div.find('p', class_='total-crimes').text.strip() if stats_div.find('p', class_='total-crimes') else "Not found"
            year = stats_div.find('span', class_='year').text.strip() if stats_div.find('span', class_='year') else "Not found"
            
            return {
                "total_reported_crimes": total_crimes,
                "year": year
            }
    except Exception as e:
        st.error(f"Failed to fetch crime statistics: {str(e)}")
        return {"error": "Failed to fetch crime statistics"}
    
    return {"error": "Failed to parse crime statistics"}
