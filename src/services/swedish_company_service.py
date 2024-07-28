# src/services/swedish_company_service.py

import time
import random
import requests  # Add this import
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from src.utils.caching import cached_get_request
from src.utils.rate_limiter import RateLimiter
import streamlit as st

allabolag_limiter = RateLimiter(calls=3, period=60)

def fetch_swedish_company_info(company_name: str, max_retries=3) -> dict:
    allabolag_limiter.wait()
    url = f"https://www.allabolag.se/what/{company_name}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    
    for attempt in range(max_retries):
        try:
            response = cached_get_request(url, headers=headers)
            
            # Check if the response is a requests.Response object
            if not isinstance(response, requests.Response):
                raise ValueError("Unexpected response type from cached_get_request")
            
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            company_div = soup.find('div', class_='companies-list')
            if company_div:
                company_link = company_div.find('a', class_='company-link')
                if company_link:
                    company_url = "https://www.allabolag.se" + company_link['href']
                    company_response = cached_get_request(company_url, headers=headers)
                    
                    # Check if the company_response is a requests.Response object
                    if not isinstance(company_response, requests.Response):
                        raise ValueError("Unexpected response type from cached_get_request for company page")
                    
                    company_response.raise_for_status()
                    company_soup = BeautifulSoup(company_response.content, 'html.parser')
                    
                    name = company_soup.find('h1', class_='company-name')
                    name = name.text.strip() if name else "Not found"
                    
                    org_number = company_soup.find('dd', class_='company-number')
                    org_number = org_number.text.strip() if org_number else "Not found"
                    
                    company_type = company_soup.find('dd', class_='company-type')
                    company_type = company_type.text.strip() if company_type else "Not found"
                    
                    status = company_soup.find('dd', class_='company-status')
                    status = status.text.strip() if status else "Not found"
                    
                    revenue = company_soup.find('dd', class_='company-revenue')
                    revenue = revenue.text.strip() if revenue else "Not found"
                    
                    employees = company_soup.find('dd', class_='company-employees')
                    employees = employees.text.strip() if employees else "Not found"
                    
                    return {
                        "company_name": name,
                        "registration_number": org_number,
                        "company_type": company_type,
                        "status": status,
                        "revenue": revenue,
                        "employees": employees
                    }
            
            return {"error": "Company not found"}
        
        except (RequestException, ValueError) as e:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.random()
                st.warning(f"Request failed. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                st.error(f"Failed to fetch company information after {max_retries} attempts: {str(e)}")
                return {
                    "error": f"Failed to fetch company information: {str(e)}",
                    "company_name": "Not found",
                    "registration_number": "Not found",
                    "company_type": "Not found",
                    "status": "Not found",
                    "revenue": "Not found",
                    "employees": "Not found"
                }
