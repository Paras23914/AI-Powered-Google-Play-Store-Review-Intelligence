import time
import pandas as pd
from model_manager import model_manager
from preprocess_predict import preprocess_dataframe
import torch
from statistics import generate_statistics
BATCH_SIZE = 64

def predict_deberta(df):

    print("\nRunning DeBERTa Models...")

    texts = df["clean_content_llm"].tolist()

    all_sentiments = []
    all_themes = []

    device = model_manager.device

    tokenizer = model_manager.sentiment_tokenizer

    for i in range(0, len(texts), BATCH_SIZE):

        batch = texts[i:i + BATCH_SIZE]

        # Tokenize Batch
        inputs = tokenizer(
            batch,
            padding=True,
            truncation=True,
            max_length=256,
            return_tensors="pt"
        )
        # Move To GPU
        inputs = {
            key: value.to(device)
            for key, value in inputs.items()
        }

        # Sentiment Prediction
        with torch.inference_mode():
        
            sentiment_output = (
                model_manager.sentiment_deberta(**inputs)
            )

            theme_output = (
                model_manager.theme_deberta(**inputs)
            )
        # Theme Prediction

        # ---------------------------------------
        # Decode Sentiment
        # ---------------------------------------

        sentiment_ids = torch.argmax(
            sentiment_output.logits,
            dim=1
        ).cpu().numpy()

        sentiment_labels = (
            model_manager.sentiment_encoder
            .inverse_transform(sentiment_ids)
        )

        all_sentiments.extend(sentiment_labels)

        # ---------------------------------------
        # Decode Theme
        # ---------------------------------------

        theme_ids = torch.argmax(
            theme_output.logits,
            dim=1
        ).cpu().numpy()

        theme_labels = (
            model_manager.theme_encoder
            .inverse_transform(theme_ids)
        )

        all_themes.extend(theme_labels)

    print("✓ DeBERTa Models Completed")
    return all_sentiments, all_themes

def predict_dataframe(df: pd.DataFrame):
    start_time = time.perf_counter()
    print("=" * 60)
    print("Prediction Pipeline Started")
    print("=" * 60)

    print(f"Reviews Received : {len(df)}")

    # -------------------------------
    # Preprocessing
    # -------------------------------

    df = preprocess_dataframe(df)

    print("\nPreprocessing Completed")

    print("\nRunning Traditional ML Models...")

    # TF-IDF (Only Once)
    X = model_manager.tfidf.transform(df["clean_content_ml"])

    # Sentiment
    X_sentiment = model_manager.sentiment_selector.transform(X)

    df["ml_sentiment"] = (
        model_manager.sentiment_model.predict(X_sentiment)
    )

    print("✓ Traditional Sentiment Completed")

    # Theme
    X_theme = model_manager.theme_selector.transform(X)

    df["ml_theme"] = (
        model_manager.theme_model.predict(X_theme)
    )

    print("✓ Traditional Theme Completed")

    # print(df[[
    #     "rating",
    #     "content",
    #     "ml_sentiment",
    #     "ml_theme"
    # ]].head())

    bert_sentiment, bert_theme = predict_deberta(df)

    df["bert_sentiment"] = bert_sentiment
    df["bert_theme"] = bert_theme
    processing_time = round(
        time.perf_counter() - start_time,
        2
    )
    if model_manager.device.type == "cuda" and torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(
            model_manager.device.index or 0
        )

    else:

        device_name = "CPU"


    statistics = generate_statistics(
        df=df,
        processing_time=processing_time,
        device=device_name,
        batch_size=BATCH_SIZE
    )

    print("\nStatistics")

    print(statistics)
    # print(
    #     df[
    #         [
    #             "rating",
    #             "content",
    #             "ml_sentiment",
    #             "bert_sentiment",
    #             "ml_theme",
    #             "bert_theme"
    #         ]
    #     ].head()
    # )

    print(f"✓ Traditional ML Predictions Generated")
    print(f"✓ DeBERTa Predictions Generated")
    return df, statistics