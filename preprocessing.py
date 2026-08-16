import pandas as pd
import re
import nltk
from nltk.corpus import stopwords

# Download stopwords if not available
try:
    stopwords.words("english")
except LookupError:
    nltk.download("stopwords")

# ==========================================
# CONFIGURATION
# ==========================================

INPUT_FILE = "data/reviews.csv"
OUTPUT_FILE = "data/clean_reviews.csv"

# ==========================================
# LOAD DATASET
# ==========================================

print("=" * 60)
print("Loading Dataset...")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

# Keep only required columns
df = df[["content", "score"]]

print(f"\nTotal Reviews: {len(df)}")

# ==========================================
# REMOVE DUPLICATES
# ==========================================

duplicates = df["content"].duplicated().sum()

print(f"Duplicate Reviews Found: {duplicates}")

df = df.drop_duplicates(subset=["content"]).reset_index(drop=True)

print(f"Reviews after removing duplicates: {len(df)}")

# ==========================================
# PREPROCESSING
# ==========================================

stop_words = set(stopwords.words("english"))

# Keep important sentiment words
stop_words.discard("not")
stop_words.discard("no")
stop_words.discard("never")


def clean_text_ml(text):
    """Cleaning for Machine Learning"""

    if pd.isna(text):
        return ""

    text = text.lower()

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

    if pd.isna(text):
        return ""

    # Remove URLs only
    text = re.sub(r"http\S+|www\S+", "", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


# Create both cleaned columns
df["clean_content_ml"] = df["content"].apply(clean_text_ml)
df["clean_content_llm"] = df["content"].apply(clean_text_llm)

# ==========================================
# SAMPLE OUTPUT
# ==========================================

print("\nSample Reviews")

for i in range(5):
    print("-" * 60)
    print("Original :", df.loc[i, "content"])
    print("ML       :", df.loc[i, "clean_content_ml"])
    print("LLM      :", df.loc[i, "clean_content_llm"])

# ==========================================
# SAVE DATASET
# ==========================================

df.to_csv(OUTPUT_FILE, index=False)

print("\nDataset saved successfully!")
print(f"Output File: {OUTPUT_FILE}")