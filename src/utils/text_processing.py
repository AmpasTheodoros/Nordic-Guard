# src/utils/text_processing.py

import re
from typing import List
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

nltk.download('vader_lexicon', quiet=True)

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_skills(text: str) -> List[str]:
    skills_list = ['python', 'java', 'c++', 'javascript', 'html', 'css', 'sql', 'machine learning', 
                   'data analysis', 'web development', 'api', 'cloud computing', 'devops']
    return [skill for skill in skills_list if skill in text.lower()]

def analyze_sentiment(text: str) -> dict:
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(text)