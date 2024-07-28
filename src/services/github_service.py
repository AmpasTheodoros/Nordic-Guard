# src/services/github_service.py

import re  # Add this import at the top of the file
from bs4 import BeautifulSoup
from src.utils.caching import cached_get_request
from src.utils.rate_limiter import RateLimiter
import streamlit as st

github_limiter = RateLimiter(calls=5, period=60)

def scrape_github_profile(username: str) -> dict:
    github_limiter.wait()
    url = f"https://github.com/{username}"
    try:
        response = cached_get_request(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        name = soup.find('span', class_='p-name')
        name = name.text.strip() if name else "Not found"
        
        bio = soup.find('div', class_='p-note')
        bio = bio.text.strip() if bio else "Not found"
        
        location = soup.find('span', class_='p-label')
        location = location.text.strip() if location else "Not found"
        
        repositories = soup.find('span', class_='Counter', text=re.compile(r'\d+'))
        repositories = repositories.text.strip() if repositories else "Not found"
        
        followers = soup.find('a', href=f"/{username}?tab=followers")
        followers = followers.find('span', class_='text-bold').text.strip() if followers else "Not found"
        
        return {
            "username": username,
            "name": name,
            "bio": bio,
            "location": location,
            "repositories": repositories,
            "followers": followers
        }
    except Exception as e:
        st.error(f"Failed to fetch GitHub profile: {str(e)}")
        return {
            "error": "Failed to fetch GitHub profile",
            "username": username,
            "name": "Not found",
            "bio": "Not found",
            "location": "Not found",
            "repositories": "Not found",
            "followers": "Not found"
        }
