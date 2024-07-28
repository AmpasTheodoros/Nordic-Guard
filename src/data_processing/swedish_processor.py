# src/data_processing/swedish_processor.py

import pandas as pd

def process_swedish_data(company_data: dict, population_data: dict, crime_data: dict) -> pd.DataFrame:
    combined_data = {
        "Company Name": company_data.get('company_name', 'N/A'),
        "Company Registration Number": company_data.get('registration_number', 'N/A'),
        "Company Type": company_data.get('company_type', 'N/A'),
        "Company Status": company_data.get('status', 'N/A'),
        "Company Revenue": company_data.get('revenue', 'N/A'),
        "Company Employees": company_data.get('employees', 'N/A'),
        "Total Population": population_data.get('total_population', 'N/A'),
        "Total Reported Crimes": crime_data.get('total_reported_crimes', 'N/A'),
        "Crime Statistics Year": crime_data.get('year', 'N/A')
    }
    return pd.DataFrame([combined_data])