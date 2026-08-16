
"""
PROJECT AUDIT SCRIPT
====================
Put this file in your BACKEND / PROJECT ROOT and run:

    python project_audit.py

It is designed to collect the information we need for the PPT:
- dataset sizes and distributions
- labelled dataset structure
- preprocessing evidence
- TF-IDF / feature-selection settings
- traditional model names
- DeBERTa model names
- Python source snippets related to splitting, labeling and evaluation
- analysis_results.csv structure and sample
- clean_reviews_161.csv / labelled_reviews.csv / other CSVs

IMPORTANT:
This script READS files and loads saved models where possible.
It does NOT retrain models, change datasets, or modify your project.
"""

from pathlib import Path
import sys
import json
import re
import traceback
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "Data"

print("=" * 90)
print("PROJECT AUDIT — PPT EVIDENCE COLLECTION")
print("=" * 90)
print("Project root:", ROOT)
print("Data folder :", DATA_DIR)
print()

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def section(title):
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)

def safe_read_csv(path):
    try:
        return pd.read_csv(path, low_memory=False)
    except Exception as e:
        print(f"ERROR reading {path}: {e}")
        return None

def print_distribution(df, col):
    if col in df.columns:
        print(f"\n{col} distribution:")
        print(df[col].value_counts(dropna=False).to_string())

def print_columns(df):
    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print("Column names:")
    for c in df.columns:
        print("  -", c)

# ---------------------------------------------------------------------
# 1. ALL CSV DATASETS
# ---------------------------------------------------------------------

section("1. DATASET INVENTORY")

csv_files = sorted(DATA_DIR.glob("*.csv")) if DATA_DIR.exists() else []

if not csv_files:
    print("No CSV files found in:", DATA_DIR)
else:
    for path in csv_files:
        print("\n---", path.name, "---")
        df = safe_read_csv(path)
        if df is None:
            continue

        print("Rows:", len(df))
        print("Columns:", len(df.columns))
        print("Columns:", list(df.columns))

        for col in ["rating", "content", "review", "sentiment", "theme",
                    "ml_sentiment", "ml_theme", "bert_sentiment",
                    "bert_theme", "summary", "reason"]:
            if col in df.columns:
                print_distribution(df, col)

# ---------------------------------------------------------------------
# 2. LABELLED REVIEWS — DETAILED
# ---------------------------------------------------------------------

section("2. LABELLED DATASET — DETAILED")

label_candidates = [
    DATA_DIR / "labelled_reviews.csv",
    DATA_DIR / "labelled_review.csv",
]

label_path = next((p for p in label_candidates if p.exists()), None)

if label_path:
    df = safe_read_csv(label_path)

    if df is not None:
        print("FILE:", label_path)
        print_columns(df)

        if "rating" in df.columns:
            print("\nRating distribution:")
            print(df["rating"].value_counts(dropna=False).sort_index().to_string())

        for col in ["sentiment", "theme"]:
            if col in df.columns:
                print_distribution(df, col)

        if "content" in df.columns:
            print("\nMissing content:", df["content"].isna().sum())
            print(
                "Empty content:",
                (df["content"].astype(str).str.strip() == "").sum()
            )

        print("\nDuplicate complete rows:", df.duplicated().sum())

        if "content" in df.columns:
            print("Duplicate content values:", df["content"].duplicated().sum())

        print("\nFirst 5 labelled records:")
        print(df.head(5).to_string(index=False))

else:
    print("labelled_reviews.csv not found.")

# ---------------------------------------------------------------------
# 3. ANALYSIS RESULTS — WEBSITE OUTPUT
# ---------------------------------------------------------------------

section("3. ANALYSIS RESULTS")

analysis_path = DATA_DIR / "analysis_results.csv"

if analysis_path.exists():
    df = safe_read_csv(analysis_path)

    if df is not None:
        print("FILE:", analysis_path)
        print_columns(df)

        for col in ["rating", "ml_sentiment", "ml_theme",
                    "bert_sentiment", "bert_theme",
                    "sentiment", "theme"]:
            if col in df.columns:
                print_distribution(df, col)

        print("\nFirst 10 rows:")
        print(df.head(10).to_string(index=False))

else:
    print("analysis_results.csv not found.")

# ---------------------------------------------------------------------
# 4. CLEAN 161 DATASET
# ---------------------------------------------------------------------

section("4. 161-REVIEW LLM DATASET")

for name in ["clean_reviews_161.csv", "clean_reviews.csv"]:
    path = DATA_DIR / name
    if path.exists():
        df = safe_read_csv(path)
        if df is not None:
            print("\nFILE:", path)
            print_columns(df)
            if "rating" in df.columns:
                print_distribution(df, "rating")
            for col in ["sentiment", "theme", "ml_sentiment", "ml_theme",
                        "bert_sentiment", "bert_theme"]:
                if col in df.columns:
                    print_distribution(df, col)
            print("\nFirst 5 rows:")
            print(df.head(5).to_string(index=False))

# ---------------------------------------------------------------------
# 5. SAVED TRADITIONAL MODELS
# ---------------------------------------------------------------------

section("5. SAVED MODEL INSPECTION")

try:
    import joblib

    model_dir = ROOT / "Models"

    model_files = [
        "tfidf.pkl",
        "selector_sentiment.pkl",
        "selector_theme.pkl",
        "sentiment_svm.pkl",
        "theme_svm.pkl",
    ]

    for filename in model_files:
        path = model_dir / filename

        if not path.exists():
            print(f"\nMISSING: {path}")
            continue

        print(f"\n--- {filename} ---")

        try:
            obj = joblib.load(path)
            print("Python type:", type(obj))
            print("Class:", type(obj).__name__)

            # TF-IDF
            if filename == "tfidf.pkl":
                for attr in [
                    "max_features",
                    "min_df",
                    "max_df",
                    "ngram_range",
                    "sublinear_tf",
                    "lowercase",
                    "strip_accents",
                    "stop_words",
                ]:
                    if hasattr(obj, attr):
                        print(f"{attr}:", getattr(obj, attr))

                if hasattr(obj, "vocabulary_"):
                    print("Vocabulary size:", len(obj.vocabulary_))

            # Selectors
            if "selector" in filename:
                for attr in ["k", "score_func"]:
                    if hasattr(obj, attr):
                        print(f"{attr}:", getattr(obj, attr))

                if hasattr(obj, "get_support"):
                    try:
                        print("Selected features:", int(obj.get_support().sum()))
                    except Exception:
                        pass

            # Classifiers
            if "svm" in filename:
                for attr in ["C", "kernel", "class_weight", "max_iter"]:
                    if hasattr(obj, attr):
                        print(f"{attr}:", getattr(obj, attr))

        except Exception as e:
            print("Could not load:", e)

except Exception as e:
    print("joblib inspection failed:", e)

# ---------------------------------------------------------------------
# 6. MODEL MANAGER — ACTUAL RUNTIME MODELS
# ---------------------------------------------------------------------

section("6. MODEL MANAGER — ACTUAL RUNTIME MODELS")

try:
    from model_manager import model_manager

    print("Device:", model_manager.device)

    print("\nTraditional sentiment model:")
    print("  Type:", type(model_manager.sentiment_model).__name__)

    print("\nTraditional theme model:")
    print("  Type:", type(model_manager.theme_model).__name__)

    print("\nTF-IDF type:")
    print(" ", type(model_manager.tfidf).__name__)

    print("\nSentiment selector:")
    print(" ", type(model_manager.sentiment_selector).__name__)

    print("\nTheme selector:")
    print(" ", type(model_manager.theme_selector).__name__)

    print("\nSentiment DeBERTa:")
    print("  Type:", type(model_manager.sentiment_deberta).__name__)

    print("\nTheme DeBERTa:")
    print("  Type:", type(model_manager.theme_deberta).__name__)

    for name, model in [
        ("Sentiment DeBERTa", model_manager.sentiment_deberta),
        ("Theme DeBERTa", model_manager.theme_deberta),
    ]:
        print(f"\n{name} config:")
        try:
            cfg = model.config
            for attr in [
                "model_type",
                "architectures",
                "num_labels",
                "id2label",
                "label2id",
                "hidden_size",
                "num_hidden_layers",
            ]:
                if hasattr(cfg, attr):
                    print(f"  {attr}:", getattr(cfg, attr))
        except Exception as e:
            print("  Config error:", e)

    for name, encoder in [
        ("Sentiment encoder", model_manager.sentiment_encoder),
        ("Theme encoder", model_manager.theme_encoder),
    ]:
        print(f"\n{name}:")
        try:
            print("  Classes:", list(encoder.classes_))
        except Exception as e:
            print("  Error:", e)

except Exception as e:
    print("Could not import model_manager.")
    print("ERROR:", e)
    traceback.print_exc()

# ---------------------------------------------------------------------
# 7. PYTHON SOURCE CODE SCAN
# ---------------------------------------------------------------------

section("7. SOURCE-CODE EVIDENCE SCAN")

keywords = [
    "train_test_split",
    "Stratified",
    "stratify",
    "TfidfVectorizer",
    "SelectKBest",
    "chi2",
    "LinearSVC",
    "LogisticRegression",
    "RandomForestClassifier",
    "DecisionTreeClassifier",
    "MultinomialNB",
    "SVC",
    "gemma",
    "gemma3",
    "ollama",
    "prompt",
    "label",
    "sentiment",
    "theme",
    "classification_report",
    "confusion_matrix",
    "accuracy_score",
    "f1_score",
]

py_files = [
    p for p in ROOT.rglob("*.py")
    if ".venv" not in p.parts
    and "venv" not in p.parts
    and "__pycache__" not in p.parts
]

print("Python files found:", len(py_files))

for path in py_files:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue

    hits = []

    for keyword in keywords:
        if keyword.lower() in text.lower():
            hits.append(keyword)

    if not hits:
        continue

    print("\n" + "-" * 90)
    print("FILE:", path.relative_to(ROOT))
    print("KEYWORDS:", ", ".join(hits))

    lines = text.splitlines()

    # Print compact context around relevant lines.
    printed_ranges = []

    for i, line in enumerate(lines):
        low = line.lower()

        if any(k.lower() in low for k in hits):
            start = max(0, i - 3)
            end = min(len(lines), i + 5)

            # avoid repeating overlapping ranges
            overlap = any(
                not (end < s or start > e)
                for s, e in printed_ranges
            )

            if not overlap:
                printed_ranges.append((start, end))

                print(f"\nLines {start + 1}-{end}:")
                for n in range(start, end):
                    print(f"{n + 1:4}: {lines[n]}")

# ---------------------------------------------------------------------
# 8. SEARCH FOR TRAIN / TEST COUNTS IN PROJECT FILES
# ---------------------------------------------------------------------

section("8. TRAIN / TEST COUNT EVIDENCE")

count_patterns = [
    r"11[, ]?807",
    r"2[, ]?342",
    r"2[, ]?361",
    r"9[, ]?446",
    r"11807",
    r"2342",
    r"2361",
    r"9446",
]

found_any = False

for path in py_files:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue

    lines = text.splitlines()

    for i, line in enumerate(lines):
        if any(re.search(pattern, line) for pattern in count_patterns):
            found_any = True
            print("\nFILE:", path.relative_to(ROOT))
            for n in range(max(0, i - 3), min(len(lines), i + 4)):
                print(f"{n + 1:4}: {lines[n]}")

if not found_any:
    print("No hard-coded dataset counts found in Python source.")

# ---------------------------------------------------------------------
# 9. QUICK PROJECT FILE INVENTORY
# ---------------------------------------------------------------------

section("9. PROJECT FILE INVENTORY")

for path in sorted(ROOT.rglob("*")):
    if not path.is_file():
        continue

    if any(part in {".git", ".venv", "venv", "__pycache__", "node_modules"} for part in path.parts):
        continue

    try:
        relative = path.relative_to(ROOT)
    except Exception:
        continue

    print(relative)

# ---------------------------------------------------------------------
# DONE
# ---------------------------------------------------------------------

section("AUDIT COMPLETE")

print("""
IMPORTANT:
Send me the ENTIRE terminal output from this script.

Do not summarize it.
Do not remove confusing sections.
Do not edit numbers.

If the output is very large, save it with:

    python project_audit.py > project_audit_output.txt

and send me project_audit_output.txt.
""")
