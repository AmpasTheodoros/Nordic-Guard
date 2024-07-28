# streamlit_app.py

import streamlit as st
import pyrebase
from src.config import firebase_config
from src.services import github_service, holiday_service, joke_service
from src.services import swedish_company_service, swedish_population_service, swedish_crime_service
from src.data_processing import individual_processor, swedish_processor

# Initialize Firebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state.user = user
            st.session_state.logged_in = True
            st.experimental_rerun()
        except:
            st.error("Invalid email or password")

def signup():
    st.subheader("Create New Account")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        try:
            user = auth.create_user_with_email_and_password(email, password)
            st.success("Account created successfully!")
            st.session_state.user = user
            st.session_state.logged_in = True
            st.experimental_rerun()
        except:
            st.error("Error creating account")

def logout():
    st.session_state.user = None
    st.session_state.logged_in = False
    st.success("Logged out successfully!")
    st.experimental_rerun()

def main_page():
    st.title("Welcome to Simple Background Check System")
    st.write("This application allows you to perform simple background checks using publicly available data.")
    st.write("Please log in or sign up to access the dashboard and perform background checks.")

    choice = st.selectbox("Login/Signup", ["Login", "Sign Up"])
    if choice == "Login":
        login()
    else:
        signup()

def dashboard():
    st.title("Background Check Dashboard")
    st.write(f"Welcome, {st.session_state.user['email']}!")

    tab1, tab2 = st.tabs(["Individual Check", "Swedish Company Check"])

    with tab1:
        github_username = st.text_input("Enter GitHub Username")
        country_code = st.text_input("Enter Country Code (e.g., US, GB, SE)", max_chars=2)

        if st.button("Run Individual Background Check"):
            if github_username and country_code:
                with st.spinner("Collecting and processing data..."):
                    try:
                        github_data = github_service.scrape_github_profile(github_username)
                        holiday_data = holiday_service.fetch_public_holidays(country_code)
                        joke_data = joke_service.fetch_random_joke()
                        
                        processed_data = individual_processor.process_data(github_data, holiday_data, joke_data)
                        
                        st.success("Data processing complete!")
                        
                        st.subheader("Processed Data")
                        st.dataframe(processed_data)
                        
                        st.subheader("Insights")
                        st.write(f"Top skills: {processed_data['Skills'].iloc[0]}")
                        st.write(f"Bio sentiment: {processed_data['Bio Sentiment'].iloc[0]:.2f} (Positive > 0.05, Negative < -0.05)")
                        st.write(f"Repositories: {processed_data['Repositories'].iloc[0]}")
                        st.write(f"Followers: {processed_data['Followers'].iloc[0]}")
                        
                    except Exception as e:
                        st.error(f"An error occurred during data processing: {str(e)}")
                        st.exception(e)
            else:
                st.warning("Please enter both a GitHub username and a country code.")

    with tab2:
        company_name = st.text_input("Enter Swedish Company Name")
        
        if st.button("Run Swedish Company Check"):
            if company_name:
                with st.spinner("Collecting and processing Swedish data..."):
                    try:
                        company_data = swedish_company_service.fetch_swedish_company_info(company_name)
                        
                        if "error" in company_data:
                            st.error(company_data["error"])
                        else:
                            st.success("Swedish company data retrieved successfully!")
                            st.write(f"Company Name: {company_data['company_name']}")
                            st.write(f"Org.nummer: {company_data['org_nummer']}")
                            
                            # Fetch additional data if needed
                            population_data = swedish_population_service.fetch_swedish_population_data()
                            crime_data = swedish_crime_service.fetch_swedish_crime_stats()
                            
                            st.subheader("Additional Swedish Data")
                            st.write(f"Total Population: {population_data.get('total_population', 'N/A')}")
                            st.write(f"Total Reported Crimes: {crime_data.get('total_reported_crimes', 'N/A')} ({crime_data.get('year', 'N/A')})")
                        
                    except Exception as e:
                        st.error(f"An error occurred during Swedish data processing: {str(e)}")
                        st.exception(e)
            else:
                st.warning("Please enter a Swedish company name.")

    if st.button("Log Out"):
        logout()

def main():
    if st.session_state.logged_in:
        dashboard()
    else:
        main_page()

if __name__ == "__main__":
    main()