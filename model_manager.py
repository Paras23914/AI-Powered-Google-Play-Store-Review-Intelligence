import os
import joblib
import torch

from transformers import (
    AutoTokenizer,
    DebertaV2ForSequenceClassification
)


class ModelManager:

    def __init__(self):

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        print("=" * 60)
        print("Loading Models...")
        print("=" * 60)

        if torch.cuda.is_available():
            print(f"GPU : {torch.cuda.get_device_name(0)}")
        else:
            print("Running on CPU")

        self.load_traditional_models()

        self.load_deberta_models()

        print("=" * 60)
        print("All Models Loaded Successfully")
        print("=" * 60)

    # ==========================================================
    # Traditional ML Models
    # ==========================================================

    def load_traditional_models(self):

        model_path = "Models"

        print("\nLoading Traditional Models...\n")

        self.tfidf = joblib.load(
            os.path.join(model_path, "tfidf.pkl")
        )
        print("✓ TF-IDF")

        self.sentiment_selector = joblib.load(
            os.path.join(model_path, "selector_sentiment.pkl")
        )
        print("✓ Sentiment Selector")

        self.theme_selector = joblib.load(
            os.path.join(model_path, "selector_theme.pkl")
        )
        print("✓ Theme Selector")

        self.sentiment_model = joblib.load(
            os.path.join(model_path, "sentiment_svm.pkl")
        )
        print("✓ Sentiment Linear SVM")

        self.theme_model = joblib.load(
            os.path.join(model_path, "theme_svm.pkl")
        )
        print("✓ Theme Linear SVM")

    # ==========================================================
    # DeBERTa Models
    # ==========================================================

    def load_deberta_models(self):

        print("\nLoading DeBERTa Models...\n")

        sentiment_path = "deberta_models/sentiment"

        self.sentiment_tokenizer = AutoTokenizer.from_pretrained(
            sentiment_path
        )

        self.sentiment_deberta = (
            DebertaV2ForSequenceClassification
            .from_pretrained(sentiment_path)
            .to(self.device)
        )

        self.sentiment_deberta.eval()

        self.sentiment_encoder = joblib.load(
            os.path.join(
                sentiment_path,
                "label_encoder.pkl"
            )
        )

        print("✓ Sentiment DeBERTa")

        theme_path = "deberta_models/theme"

        self.theme_tokenizer = AutoTokenizer.from_pretrained(
            theme_path
        )

        self.theme_deberta = (
            DebertaV2ForSequenceClassification
            .from_pretrained(theme_path)
            .to(self.device)
        )

        self.theme_deberta.eval()

        self.theme_encoder = joblib.load(
            os.path.join(
                theme_path,
                "label_encoder.pkl"
            )
        )

        print("✓ Theme DeBERTa")


# ==========================================================
# Global Instance
# ==========================================================

model_manager = ModelManager()