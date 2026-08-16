import re
import pandas as pd
import nltk
from nltk.corpus import stopwords

# Download stopwords if needed
try:
    stopwords.words("english")
except LookupError:
    nltk.download("stopwords")

# Stopwords
stop_words = set(stopwords.words("english"))

# Keep important sentiment words
stop_words.discard("not")
stop_words.discard("no")
stop_words.discard("never")


def clean_text_ml(text):
    """
    Cleaning for Traditional ML Models
    """

    if pd.isna(text):
        return ""

    text = str(text).lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)

    # Remove punctuation
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    # Remove stopwords
    words = text.split()
    words = [word for word in words if word not in stop_words]

    return " ".join(words)


def clean_text_llm(text):
    """
    Cleaning for DeBERTa
    """

    if pd.isna(text):
        return ""

    text = str(text)

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def preprocess_dataframe(df):
    """
    Prepare uploaded dataframe for prediction.
    """

    # Validate required columns
    required_columns = ["rating", "content"]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(missing)}"
        )

    # Remove empty rows
    df = df.dropna(subset=["rating", "content"]).copy()

    # Convert to correct datatype
    df["content"] = df["content"].astype(str)

    # Create cleaned columns
    df["clean_content_ml"] = df["content"].apply(clean_text_ml)

    df["clean_content_llm"] = df["content"].apply(clean_text_llm)

    return df