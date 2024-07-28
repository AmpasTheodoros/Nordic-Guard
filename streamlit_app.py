import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from typing import Dict, Any, List
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

# Download necessary NLTK data
nltk.download('vader_lexicon', quiet=True)

def scrape_github_profile(username: str) -> Dict[str, Any]:
    """Scrape public GitHub profile information."""
    url = f"https://github.com/{username}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    name = soup.find('span', class_='p-name')
    name = name.text.strip() if name else "Not found"
    
    bio = soup.find('div', class_='p-note')
    bio = bio.text.strip() if bio else "Not found"
    
    location = soup.find('span', class_='p-label')
    location = location.text.strip() if location else "Not found"
    
    return {"username": username, "name": name, "bio": bio, "location": location}

def fetch_public_holidays(country_code: str) -> Dict[str, Any]:
    """Fetch public holidays using the Nager.Date API."""
    current_year = pd.Timestamp.now().year
    url = f"https://date.nager.at/api/v3/PublicHolidays/{current_year}/{country_code}"
    
    response = requests.get(url)
    if response.status_code == 200:
        holidays = response.json()
        return {
            "country": country_code,
            "year": current_year,
            "holidays": [f"{h['date']} - {h['name']}" for h in holidays[:5]]
        }
    return {"error": "Failed to fetch public holidays"}

def fetch_random_joke() -> Dict[str, str]:
    """Fetch a random joke using the Official Joke API."""
    url = "https://official-joke-api.appspot.com/random_joke"
    response = requests.get(url)
    if response.status_code == 200:
        joke = response.json()
        return {"setup": joke['setup'], "punchline": joke['punchline']}
    return {"error": "Failed to fetch joke"}

def clean_text(text: str) -> str:
    """Clean and normalize text data."""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_skills(text: str) -> List[str]:
    """Extract potential skills from text using a predefined list."""
    skills_list = ['python', 'java', 'c++', 'javascript', 'html', 'css', 'sql', 'machine learning', 
                   'data analysis', 'web development', 'api', 'cloud computing', 'devops']
    return [skill for skill in skills_list if skill in text.lower()]

def analyze_sentiment(text: str) -> Dict[str, float]:
    """Analyze sentiment of text using NLTK's SentimentIntensityAnalyzer."""
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(text)

def process_github_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process and enrich GitHub profile data."""
    processed_data = data.copy()
    processed_data['clean_bio'] = clean_text(data['bio'])
    processed_data['skills'] = extract_skills(data['bio'])
    processed_data['skill_count'] = len(processed_data['skills'])
    processed_data['bio_sentiment'] = analyze_sentiment(data['bio'])
    return processed_data

def process_holiday_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process holiday data."""
    processed_data = data.copy()
    holiday_dates = [holiday.split(' - ')[0] for holiday in data['holidays']]
    holiday_names = [holiday.split(' - ')[1] for holiday in data['holidays']]
    
    processed_data['holiday_count'] = len(holiday_dates)
    processed_data['first_holiday'] = min(holiday_dates) if holiday_dates else None
    processed_data['last_holiday'] = max(holiday_dates) if holiday_dates else None
    
    holiday_sentiments = [analyze_sentiment(name)['compound'] for name in holiday_names]
    processed_data['avg_holiday_sentiment'] = np.mean(holiday_sentiments) if holiday_sentiments else 0
    
    return processed_data

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate cosine similarity between two texts."""
    vectorizer = TfidfVectorizer().fit_transform([text1, text2])
    return cosine_similarity(vectorizer[0], vectorizer[1])[0][0]

def create_visualizations(data: pd.DataFrame) -> Dict[str, Any]:
    """Create visualizations based on the processed data."""
    visualizations = {}
    
    if 'bio_sentiment' in data.columns and isinstance(data['bio_sentiment'].iloc[0], dict):
        fig, ax = plt.subplots()
        sentiment_data = data['bio_sentiment'].iloc[0]
        sns.barplot(x=list(sentiment_data.keys()), y=list(sentiment_data.values()), ax=ax)
        ax.set_title('Bio Sentiment Distribution')
        ax.set_ylabel('Score')
        visualizations['sentiment_dist'] = fig
    
    if 'skills' in data.columns and data['skills'].iloc[0]:
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(data['skills'].iloc[0]))
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('Skills Word Cloud')
        visualizations['skills_wordcloud'] = fig
    
    return visualizations

def advanced_data_processing(github_data: Dict[str, Any], holiday_data: Dict[str, Any], joke_data: Dict[str, str]) -> pd.DataFrame:
    """Perform advanced data processing on collected data."""
    processed_github = process_github_data(github_data)
    processed_holidays = process_holiday_data(holiday_data)
    
    combined_data = {
        "GitHub Username": github_data['username'],
        "Name": github_data['name'],
        "Location": github_data['location'],
        "Bio": github_data['bio'],
        "Clean Bio": processed_github['clean_bio'],
        "Skills": processed_github['skills'],
        "Skill Count": processed_github['skill_count'],
        "Bio Sentiment": processed_github['bio_sentiment'],
        "Country": holiday_data['country'],
        "Holiday Count": processed_holidays['holiday_count'],
        "First Holiday": processed_holidays['first_holiday'],
        "Last Holiday": processed_holidays['last_holiday'],
        "Avg Holiday Sentiment": processed_holidays['avg_holiday_sentiment'],
        "Joke Setup": joke_data['setup'],
        "Joke Punchline": joke_data['punchline'],
    }
    
    df = pd.DataFrame([combined_data])
    
    if 'Clean Bio' in df.columns and 'Joke Setup' in df.columns and 'Joke Punchline' in df.columns:
        df['Bio-Joke Similarity'] = calculate_similarity(
            df['Clean Bio'].iloc[0], 
            df['Joke Setup'].iloc[0] + ' ' + df['Joke Punchline'].iloc[0]
        )
    
    return df

def main():
    st.title("Advanced Background Check System")

    github_username = st.text_input("Enter GitHub Username")
    country_code = st.text_input("Enter Country Code (e.g., US, GB, SE)", max_chars=2)

    if st.button("Run Advanced Background Check"):
        if github_username and country_code:
            with st.spinner("Collecting and processing data..."):
                try:
                    github_data = scrape_github_profile(github_username)
                    holiday_data = fetch_public_holidays(country_code)
                    joke_data = fetch_random_joke()
                    
                    processed_data = advanced_data_processing(github_data, holiday_data, joke_data)
                    
                    st.success("Data processing complete!")
                    
                    st.subheader("Processed Data")
                    st.dataframe(processed_data)
                    
                    visualizations = create_visualizations(processed_data)
                    
                    st.subheader("Visualizations")
                    for title, fig in visualizations.items():
                        st.pyplot(fig)
                    
                    st.subheader("Insights")
                    if 'Skills' in processed_data.columns:
                        st.write(f"Top skills: {', '.join(processed_data['Skills'].iloc[0])}")
                    if 'Bio Sentiment' in processed_data.columns and isinstance(processed_data['Bio Sentiment'].iloc[0], dict):
                        st.write(f"Bio sentiment: {processed_data['Bio Sentiment'].iloc[0]['compound']:.2f} (Positive > 0.05, Negative < -0.05)")
                    if 'Bio-Joke Similarity' in processed_data.columns:
                        st.write(f"Bio-Joke Similarity: {processed_data['Bio-Joke Similarity'].iloc[0]:.2f}")
                    
                except Exception as e:
                    st.error(f"An error occurred during data processing: {str(e)}")
                    st.exception(e)
        else:
            st.warning("Please enter both a GitHub username and a country code.")

if __name__ == "__main__":
    main()