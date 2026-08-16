import pandas as pd
from datetime import datetime

def generate_statistics(
    df: pd.DataFrame,
    processing_time,
    device,
    batch_size
):

    stats = {}
    # =====================================================
    # Header
    # =====================================================

    stats["header"] = {

        "analysis_completed": True,

        "analysis_time": datetime.now().strftime(
            "%d %b %Y %I:%M %p"
        )

    }
    # =====================================================
    # Dataset
    # =====================================================

    stats["dataset"] = {

        "total_reviews": len(df),

        "average_rating": float(
            round(df["rating"].mean(), 2)
        ),

        "rating_distribution": (
            df["rating"]
            .value_counts()
            .sort_index()
            .to_dict()
        )

    }

    # =====================================================
    # Performance
    # =====================================================

    stats["performance"] = {

        "processing_time": processing_time,

        "reviews_per_second": round(
            len(df) / processing_time,
            2
        ) if processing_time > 0 else 0,

        "device": device,

        "batch_size": batch_size

    }
    # =====================================================
    # Traditional ML
    # =====================================================

    traditional_sentiment = (
        df["ml_sentiment"]
        .value_counts()
        .sort_values(ascending=False)
        .to_dict()
    )

    traditional_theme = (
        df["ml_theme"]
        .value_counts()
        .sort_values(ascending=False)
        .to_dict()
    )

    stats["traditional"] = {

        "sentiment": traditional_sentiment,

        "theme": traditional_theme

    }
    traditional_priority = (
        df[
            df["ml_theme"] != "General Praise"
        ]["ml_theme"]
        .value_counts()
        .head(5)
    )

    stats["traditional"]["priority_issues"] = [

        {
            "theme": theme,
            "count": int(count)
        }

        for theme, count in traditional_priority.items()

    ]

    traditional_feedback = []

    for theme in traditional_priority.index:

        review = df[
            df["ml_theme"] == theme
        ].iloc[0]

        traditional_feedback.append({

            "theme": theme,

            "rating": int(review["rating"]),

            "review": review["content"],

            "sentiment": review["ml_sentiment"]

        })

    stats["traditional"]["representative_feedback"] = traditional_feedback
    # =====================================================
    # DeBERTa
    # =====================================================

    deberta_sentiment = (
        df["bert_sentiment"]
        .value_counts()
        .sort_values(ascending=False)
        .to_dict()
    )

    deberta_theme = (
        df["bert_theme"]
        .value_counts()
        .sort_values(ascending=False)
        .to_dict()
    )

    stats["deberta"] = {

        "sentiment": deberta_sentiment,

        "theme": deberta_theme

    }
    deberta_priority = (
        df[
            df["bert_theme"] != "General Praise"
        ]["bert_theme"]
        .value_counts()
        .head(5)
    )

    stats["deberta"]["priority_issues"] = [

        {
            "theme": theme,
            "count": int(count)
        }

        for theme, count in deberta_priority.items()

    ]
    deberta_feedback = []
    
    for theme in deberta_priority.index:
    
        review = df[
            df["bert_theme"] == theme
        ].iloc[0]
    
        deberta_feedback.append({
        
            "theme": theme,
    
            "rating": int(review["rating"]),
    
            "review": review["content"],
    
            "sentiment": review["bert_sentiment"]
    
        })
    
    stats["deberta"]["representative_feedback"] = deberta_feedback
    # =====================================================
    # Model Comparison
    # =====================================================

    sentiment_agreement = round(
        (
            df["ml_sentiment"] ==
            df["bert_sentiment"]
        ).mean() * 100,
        2
    )

    theme_agreement = round(
        (
            df["ml_theme"] ==
            df["bert_theme"]
        ).mean() * 100,
        2
    )

    stats["comparison"] = {

        "sentiment_agreement": sentiment_agreement,

        "theme_agreement": theme_agreement

    }
    # =====================================================
    # Preview
    # =====================================================

    stats["preview"] = (
        df[
            [
                "rating",
                "content",
                "ml_sentiment",
                "ml_theme",
                "bert_sentiment",
                "bert_theme"
            ]
        ]
        .head(20)
        .to_dict(
            orient="records"
        )
    )

    return stats