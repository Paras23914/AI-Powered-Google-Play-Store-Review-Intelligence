import os
import random
import joblib
import numpy as np
import pandas as pd
import torch

from datasets import Dataset

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix
)

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback
)

# ==========================================================
# CONFIGURATION
# ==========================================================

MODEL_NAME = "microsoft/deberta-v3-base"

INPUT_FILE = "data/labelled_reviews.csv"

OUTPUT_FOLDER = "deberta_models"

SENTIMENT_FOLDER = os.path.join(
    OUTPUT_FOLDER,
    "sentiment"
)

THEME_FOLDER = os.path.join(
    OUTPUT_FOLDER,
    "theme"
)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(SENTIMENT_FOLDER, exist_ok=True)
os.makedirs(THEME_FOLDER, exist_ok=True)

MAX_LENGTH = 128

BATCH_SIZE = 8

EPOCHS = 3

LEARNING_RATE = 1e-5

SEED = 42

# ==========================================================
# RANDOM SEED
# ==========================================================

def set_seed(seed):

    random.seed(seed)

    np.random.seed(seed)

    torch.manual_seed(seed)

    if torch.cuda.is_available():

        torch.cuda.manual_seed_all(seed)

# ==========================================================
# DEVICE INFORMATION
# ==========================================================

def print_device_info():

    print("=" * 60)

    print("DEVICE INFORMATION")

    print("=" * 60)

    if torch.cuda.is_available():

        print("GPU :", torch.cuda.get_device_name(0))

    else:

        print("Running on CPU")

# ==========================================================
# LOAD DATASET
# ==========================================================

def load_dataset():

    print("=" * 60)

    print("Loading Dataset...")

    print("=" * 60)

    df = pd.read_csv(INPUT_FILE)

    print(f"Total Reviews : {len(df)}")

    return df

# ==========================================================
# PREPROCESS DATASET
# ==========================================================

def prepare_dataset(df):

    df = df.dropna(subset=["clean_content_ml"])

    mapping = {

        "Data Loss": "Bug Report",
        "Data Loss/Sync Issue": "Bug Report",
        "Backup and Restore": "Bug Report",
        "Notification Failure": "Bug Report",
        "Notification Issue": "Bug Report",
        "Server Issue": "Bug Report",

        "Sync Issue": "Performance Issue",
        "Synchronization Issue": "Performance Issue",
        "Syncing Issue": "Performance Issue",
        "Sync Problem": "Performance Issue",
        "Data Sync Issue": "Performance Issue",
        "Freezing": "Performance Issue",
        "High battery usage": "Performance Issue",

        "Display Problems": "UI Problem",
        "Navigation issues": "UI Problem",

        "Password Issues": "Login Problem",

        "Payment Issue": "Subscription Issue",

        "Data leak": "Security Concern",

        "Intrusive Advertising": "Ads Complaint",
        "Annoying Pop-ups": "Ads Complaint"

    }

    df["theme"] = df["theme"].replace(mapping)

    X = df["clean_content_ml"].astype(str)

    y_sentiment = df["sentiment"]

    y_theme = df["theme"]

    return X, y_sentiment, y_theme

# ==========================================================
# LABEL ENCODING
# ==========================================================

def encode_labels(labels):

    encoder = LabelEncoder()

    encoded_labels = encoder.fit_transform(labels)

    return encoded_labels, encoder

# ==========================================================
# TRAIN TEST SPLIT
# ==========================================================

def split_dataset(X, y):

    return train_test_split(

        X,

        y,

        test_size=0.20,

        random_state=SEED,

        stratify=y

    )

# ==========================================================
# LOAD TOKENIZER
# ==========================================================

def load_tokenizer():

    print("=" * 60)

    print("Loading Tokenizer...")

    print("=" * 60)

    tokenizer = AutoTokenizer.from_pretrained(

        MODEL_NAME

    )

    return tokenizer

# ==========================================================
# TOKENIZATION
# ==========================================================

def tokenize(batch,tokenizer):

    return tokenizer(

        batch["text"],

        truncation=True,

        padding="max_length",

        max_length=MAX_LENGTH

    )

# ==========================================================
# CREATE DATASET
# ==========================================================

def create_dataset(texts, labels):

    dataset = Dataset.from_dict({

        "text": texts.tolist(),

        "label": labels.tolist()

    })

    return dataset

# ==========================================================
# METRICS
# ==========================================================

def compute_metrics(eval_pred):

    logits, labels = eval_pred

    predictions = np.argmax(

        logits,

        axis=1

    )

    accuracy = accuracy_score(

        labels,

        predictions

    )

    precision, recall, f1, _ = precision_recall_fscore_support(

        labels,

        predictions,

        average="weighted",

        zero_division=0

    )

    return {

        "accuracy": accuracy,

        "precision": precision,

        "recall": recall,

        "f1": f1

    }

# ==========================================================
# TRAIN TRANSFORMER
# ==========================================================

def train_transformer(

    train_dataset,

    test_dataset,

    tokenizer,

    num_labels,

    output_folder

):

    print("=" * 60)

    print(f"Training {output_folder}")

    print("=" * 60)

    model = AutoModelForSequenceClassification.from_pretrained(

        MODEL_NAME,

        num_labels=num_labels

    )
    print(model.config)
    batch = train_dataset[:2]

    outputs = model(
        input_ids=batch["input_ids"],
        attention_mask=batch["attention_mask"],
        labels=batch["label"]
    )
    
    print(outputs.loss)

    training_args = TrainingArguments(

        output_dir=output_folder,

        eval_strategy="epoch",

        save_strategy="epoch",

        load_best_model_at_end=True,

        metric_for_best_model="accuracy",

        greater_is_better=True,

        learning_rate=LEARNING_RATE,

        num_train_epochs=EPOCHS,

        per_device_train_batch_size=BATCH_SIZE,

        per_device_eval_batch_size=BATCH_SIZE,

        weight_decay=0.01,

        warmup_steps=100,

        gradient_accumulation_steps=1,

        max_grad_norm=1.0,

        fp16=False,

        bf16=False,

        logging_steps=50,

        save_total_limit=1,

        report_to="none",

        seed=SEED

    )

    trainer = Trainer(

        model=model,
        
        args=training_args,

        train_dataset=train_dataset,

        eval_dataset=test_dataset,

        compute_metrics=compute_metrics,

        callbacks=[

            EarlyStoppingCallback(

                early_stopping_patience=2

            )

        ]

    )

    trainer.train()

    trainer.save_model(output_folder)

    tokenizer.save_pretrained(output_folder)

    return trainer

# ==========================================================
# EVALUATE MODEL
# ==========================================================

def evaluate_model(

    trainer,

    test_dataset,

    encoder,
    output_folder,test_reviews

):

    predictions = trainer.predict(

        test_dataset

    )

    y_pred = np.argmax(

        predictions.predictions,

        axis=1

    )

    y_true = predictions.label_ids

    accuracy = accuracy_score(

        y_true,

        y_pred

    )

    print("\n" + "=" * 60)

    print("MODEL EVALUATION")

    print("=" * 60)

    print(f"Accuracy : {accuracy:.4f}\n")

    print("Classification Report\n")

    print(

        classification_report(

            encoder.inverse_transform(y_true),

            encoder.inverse_transform(y_pred),

            zero_division=0

        )

    )

    print("Confusion Matrix\n")

    print(

        confusion_matrix(

            y_true,

            y_pred

        )

    )
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        average="weighted",
        zero_division=0
    )

    report = classification_report(
        encoder.inverse_transform(y_true),
        encoder.inverse_transform(y_pred),
        output_dict=True,
        zero_division=0
    )

    cm = confusion_matrix(y_true, y_pred)
    metrics_df = pd.DataFrame({

        "Metric":[
            "Accuracy",
            "Precision",
            "Recall",
            "F1 Score"
        ],

        "Value":[
            accuracy,
            precision,
            recall,
            f1
        ]

    })
    report_df = pd.DataFrame(report).transpose()
    cm_df = pd.DataFrame(
        cm,
        index=encoder.classes_,
        columns=encoder.classes_
    )
    predictions_df = pd.DataFrame({

        "Review": test_reviews,

        "Actual": encoder.inverse_transform(y_true),

        "Predicted": encoder.inverse_transform(y_pred)

    })

    predictions_df["Correct"] = (
        predictions_df["Actual"] ==
        predictions_df["Predicted"]
    )
    with pd.ExcelWriter(

    os.path.join(output_folder, "results.xlsx")
    ) as writer:

        metrics_df.to_excel(
            writer,
            sheet_name="Metrics",
            index=False
        )

        report_df.to_excel(
            writer,
            sheet_name="Classification Report"
        )

        cm_df.to_excel(
            writer,
            sheet_name="Confusion Matrix"
        )

        predictions_df.to_excel(
            writer,
            sheet_name="Predictions",
            index=False
        )
    return accuracy
# ==========================================================
# MAIN
# ==========================================================

def main():
    set_seed(SEED)
    print_device_info()
    # ------------------------------------------------------
    # Load Dataset
    # ------------------------------------------------------

    df = load_dataset()

    X, y_sentiment, y_theme = prepare_dataset(df)

    tokenizer = load_tokenizer()

    # ======================================================
    # SENTIMENT MODEL
    # ======================================================

    print("\n" + "=" * 60)

    print("TRAINING SENTIMENT MODEL")

    print("=" * 60)

    y_sentiment_encoded, sentiment_encoder = encode_labels(

        y_sentiment

    )

    X_train, X_test, y_train, y_test = split_dataset(

        X,

        y_sentiment_encoded

    )
    test_reviews = X_test.tolist()

    train_dataset = create_dataset(

        X_train,

        y_train

    )

    test_dataset = create_dataset(

        X_test,

        y_test

    )

    train_dataset = train_dataset.map(

        lambda batch: tokenize(batch, tokenizer),

        batched=True

    )

    test_dataset = test_dataset.map(

        lambda batch: tokenize(batch, tokenizer),

        batched=True

    )

    train_dataset.set_format(

        type="torch",

        columns=[

            "input_ids",

            "attention_mask",

            "label"

        ]

    )

    test_dataset.set_format(

        type="torch",

        columns=[

            "input_ids",

            "attention_mask",

            "label"

        ]

    )

    sentiment_trainer = train_transformer(

        train_dataset,

        test_dataset,

        tokenizer,

        len(sentiment_encoder.classes_),

        SENTIMENT_FOLDER

    )

    sentiment_accuracy = evaluate_model(

        sentiment_trainer,

        test_dataset,

        sentiment_encoder,
        SENTIMENT_FOLDER,test_reviews

    )

    joblib.dump(

        sentiment_encoder,

        os.path.join(

            SENTIMENT_FOLDER,

            "label_encoder.pkl"

        )

    )

    # ======================================================
    # THEME MODEL
    # ======================================================

    print("\n" + "=" * 60)

    print("TRAINING THEME MODEL")

    print("=" * 60)

    y_theme_encoded, theme_encoder = encode_labels(

        y_theme

    )

    X_train, X_test, y_train, y_test = split_dataset(

        X,

        y_theme_encoded

    )
    test_reviews = X_test.tolist()
    train_dataset = create_dataset(

        X_train,

        y_train

    )

    test_dataset = create_dataset(

        X_test,

        y_test

    )

    train_dataset = train_dataset.map(

        lambda batch: tokenize(batch, tokenizer),

        batched=True

    )

    test_dataset = test_dataset.map(

        lambda batch: tokenize(batch, tokenizer),

        batched=True

    )

    train_dataset.set_format(

        type="torch",

        columns=[

            "input_ids",

            "attention_mask",

            "label"

        ]

    )

    test_dataset.set_format(

        type="torch",

        columns=[

            "input_ids",

            "attention_mask",

            "label"

        ]

    )

    theme_trainer = train_transformer(

        train_dataset,

        test_dataset,

        tokenizer,

        len(theme_encoder.classes_),

        THEME_FOLDER

    )

    theme_accuracy = evaluate_model(

        theme_trainer,

        test_dataset,

        theme_encoder,
        THEME_FOLDER,test_reviews

    )

    joblib.dump(

        theme_encoder,

        os.path.join(

            THEME_FOLDER,

            "label_encoder.pkl"

        )

    )

    # ======================================================
    # SUMMARY
    # ======================================================

    print("\n" + "=" * 60)

    print("TRAINING COMPLETED")

    print("=" * 60)

    print(f"Sentiment Accuracy : {sentiment_accuracy:.4f}")

    print(f"Theme Accuracy     : {theme_accuracy:.4f}")

if __name__ == "__main__":

    main()