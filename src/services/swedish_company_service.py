import requests
from bs4 import BeautifulSoup
import streamlit as st
import re

def fetch_swedish_company_info(company_name: str) -> dict:
    search_url = f"https://www.allabolag.se/what/{company_name}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    try:
        st.write(f"Fetching URL: {search_url}")
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Try to find company name and Org.nummer anywhere in the HTML
        company_name_elem = soup.find('h2', class_=lambda x: x and 'search-results__item__title' in x)
        org_nummer_elem = soup.find('dd', attrs={"data-v-2e433002": ""})

        if not company_name_elem or not org_nummer_elem:
            # If not found, try to extract from script tag
            script_tag = soup.find('script', string=re.compile('search-result-default'))
            if script_tag:
                script_content = script_tag.string
                company_match = re.search(r'"jurnamn":"([^"]+)"', script_content)
                org_nummer_match = re.search(r'"orgnr":"([^"]+)"', script_content)
                
                if company_match and org_nummer_match:
                    return {
                        "company_name": company_match.group(1),
                        "org_nummer": org_nummer_match.group(1)
                    }

            return {"error": "Company information not found"}

        company_name = company_name_elem.text.strip() if company_name_elem else "Not found"
        org_nummer = org_nummer_elem.text.strip() if org_nummer_elem else "Not found"

        return {
            "company_name": company_name,
            "org_nummer": org_nummer
        }

    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

# Streamlit app code
st.title("Swedish Company Info Fetcher")

company_name = st.text_input("Enter company name")
if st.button("Fetch Company Info"):
    if company_name:
        result = fetch_swedish_company_info(company_name)
        if "error" in result:
            st.error(result["error"])
        else:
            st.success("Company information retrieved successfully!")
            st.write(f"Company Name: {result['company_name']}")
            st.write(f"Org.nummer: {result['org_nummer']}")
    else:
        st.warning("Please enter a company name")

# Debug information
if st.checkbox("Show debug information"):
    if company_name:
        response = requests.get(f"https://www.allabolag.se/what/{company_name}")
        st.write("Response status code:", response.status_code)
        st.write("Response content preview:")
        st.code(response.text[:1000])  # Show first 1000 characters of the response