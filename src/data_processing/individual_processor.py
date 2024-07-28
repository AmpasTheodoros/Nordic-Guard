# src/data_processing/individual_processor.py

import pandas as pd
from src.utils.text_processing import clean_text, extract_skills, analyze_sentiment

def process_data(github_data: dict, holiday_data: dict, joke_data: dict) -> pd.DataFrame:
    # Check if there was an error fetching GitHub data
    if "error" in github_data:
        clean_bio = "N/A"
        skills = []
        bio_sentiment = {"compound": 0}
    else:
        clean_bio = clean_text(github_data.get('bio', ''))
        skills = extract_skills(github_data.get('bio', ''))
        bio_sentiment = analyze_sentiment(github_data.get('bio', ''))
    
    combined_data = {
        "GitHub Username": github_data.get('username', 'N/A'),
        "Name": github_data.get('name', 'N/A'),
        "Location": github_data.get('location', 'N/A'),
        "Bio": github_data.get('bio', 'N/A'),
        "Clean Bio": clean_bio,
        "Skills": ', '.join(skills),
        "Skill Count": len(skills),
        "Bio Sentiment": bio_sentiment['compound'],
        "Repositories": github_data.get('repositories', 'N/A'),
        "Followers": github_data.get('followers', 'N/A'),
        "Country": holiday_data.get('country', 'N/A'),
        "Holidays": ', '.join(holiday_data.get('holidays', [])),
        "Joke Setup": joke_data.get('setup', 'N/A'),
        "Joke Punchline": joke_data.get('punchline', 'N/A'),
    }
    
    return pd.DataFrame([combined_data])