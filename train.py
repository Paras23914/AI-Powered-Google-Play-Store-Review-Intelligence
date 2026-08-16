import os
import time
import joblib
import pandas as pd
from sklearn.model_selection import (
    train_test_split,
    GridSearchCV
)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import (
    SelectKBest,
    chi2
)
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    precision_recall_fscore_support,
    accuracy_score,
    classification_report,
    confusion_matrix
)

INPUT_FILE = "data/labelled_reviews.csv"
MODEL_FOLDER = "models/"
os.makedirs(MODEL_FOLDER, exist_ok=True)

def load_dataset():
    print("=" * 60)
    print("Loading Labelled Dataset...")
    print("=" * 60)
    df = pd.read_csv(INPUT_FILE)
    print(f"Total Reviews : {len(df)}")
    return df

def prepare_data(df):
    # Remove missing reviews
    df = df.dropna(subset=["clean_content_ml"])
    # Merge refined themes back into original categories
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

def split_data(X, y):
    return train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

def vectorize_text(X_train, X_test):
    tfidf = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        max_features=None,
        min_df=2,
        max_df=0.90,
        sublinear_tf=True,
        ngram_range=(1,2)
    )
    X_train = tfidf.fit_transform(X_train)
    X_test = tfidf.transform(X_test)
    return tfidf, X_train, X_test

def feature_selection(X_train, X_test, y_train):
    selector = SelectKBest(
        score_func=chi2,
        k='all'
    )
    X_train = selector.fit_transform(
        X_train,
        y_train
    )
    X_test = selector.transform(X_test)
    return selector, X_train, X_test

def tune_logistic_regression(X_train, y_train):
    print("=" * 60)
    print("Tuning Logistic Regression...")
    print("=" * 60)
    parameters = {
        "solver": ["saga"],
        "max_iter": [3000],
        "C": [0.01, 0.1, 0.5, 1, 2, 5, 10,20]
        
    }
    grid = GridSearchCV(
        estimator=LogisticRegression(class_weight="balanced",
    C=10,
    max_iter=3000),
        param_grid=parameters,
        cv=5,
        scoring="f1_weighted",
        n_jobs=-1,
        verbose=1
    )
    grid.fit(X_train, y_train)
    print("\nBest Parameters :", grid.best_params_)
    print("Best CV Accuracy :", round(grid.best_score_, 4))
    return grid.best_estimator_

def tune_svm(X_train, y_train):
    print("=" * 60)
    print("Tuning Linear SVM...")
    print("=" * 60)
    parameters = {
        "C": [0.001, 0.01, 0.1, 0.5, 1, 2, 5, 10,20,50]
    }
    grid = GridSearchCV(
        estimator=LinearSVC(
            C=0.5,
    class_weight="balanced"
        ),
        param_grid=parameters,
        cv=5,
        scoring="f1_weighted",
        n_jobs=-1,
        verbose=1
    )
    grid.fit(X_train, y_train)
    print("\nBest Parameters :", grid.best_params_)
    print("Best CV Accuracy :", round(grid.best_score_, 4))
    return grid.best_estimator_

def train_model(model, model_name, X_train, X_test, y_train, y_test):
    print("=" * 60)
    print(f"Training : {model_name}")
    print("=" * 60)
    start = time.time()
    model.fit(X_train, y_train)
    training_time = round(time.time() - start, 2)
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test,
        predictions,
        average="weighted",
        zero_division=0
    )
    report = classification_report(
        y_test,
        predictions,
        output_dict=True,
        zero_division=0
    )
    cm = confusion_matrix(
        y_test,
        predictions
    )
    metrics_df = pd.DataFrame({
        "Metric":[
            "Accuracy",
            "Precision",
            "Recall",
            "F1 Score",
            "Training Time (sec)"
        ],
        "Value":[
            accuracy,
            precision,
            recall,
            f1,
            training_time
        ]
    })
    report_df = pd.DataFrame(report).transpose()
    cm_df = pd.DataFrame(cm)
    predictions_df = pd.DataFrame({
        "Actual": y_test,
        "Predicted": predictions
    })
    predictions_df["Correct"] = (
        predictions_df["Actual"] ==
        predictions_df["Predicted"]
    )
    RESULT_FOLDER = "results"
    os.makedirs(RESULT_FOLDER, exist_ok=True)
    filename = model_name.replace(" ", "_") + ".xlsx"
    with pd.ExcelWriter(
        os.path.join(
            RESULT_FOLDER,
            filename
        )
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
    print(f"Accuracy      : {accuracy:.4f}")
    print(f"Training Time : {training_time} sec\n")
    print(classification_report(
        y_test,
        predictions,
        zero_division=0
    ))
    print(confusion_matrix(
        y_test,
        predictions
    ))
    return model, accuracy, training_time

def save_model(model, filename):
    path = os.path.join(
        MODEL_FOLDER,
        filename
    )
    joblib.dump(model, path)
    print(f"Saved : {filename}")

def main():
    # ==========================================================
    # LOAD DATA
    # ==========================================================
    df = load_dataset()
    X, y_sentiment, y_theme = prepare_data(df)
    # ==========================================================
    # SPLIT DATA
    # ==========================================================
    X_train_s, X_test_s, y_train_s, y_test_s = split_data(
        X,
        y_sentiment
    )
    X_train_t, X_test_t, y_train_t, y_test_t = split_data(
        X,
        y_theme
    )
    # ==========================================================
    # TF-IDF
    # ==========================================================
    tfidf, X_train_s, X_test_s = vectorize_text(
        X_train_s,
        X_test_s
    )
    X_train_t = tfidf.transform(X_train_t)
    X_test_t = tfidf.transform(X_test_t)
    # ==========================================================
    # FEATURE SELECTION
    # ==========================================================
    selector_s, X_train_s, X_test_s = feature_selection(
        X_train_s,
        X_test_s,
        y_train_s
    )
    selector_t, X_train_t, X_test_t = feature_selection(
        X_train_t,
        X_test_t,
        y_train_t
    )
    # ==========================================================
    # HYPERPARAMETER TUNING
    # ==========================================================
    best_sentiment_lr = tune_logistic_regression(
        X_train_s,
        y_train_s
    )
    best_theme_lr = tune_logistic_regression(
        X_train_t,
        y_train_t
    )
    best_sentiment_svm = tune_svm(
        X_train_s,
        y_train_s
    )
    best_theme_svm = tune_svm(
        X_train_t,
        y_train_t
    )
    # ==========================================================
    # SENTIMENT MODELS
    # ==========================================================
    sentiment_lr, sentiment_lr_acc, _ = train_model(
        best_sentiment_lr,
        "Sentiment Logistic Regression",
        X_train_s,
        X_test_s,
        y_train_s,
        y_test_s
    )
    sentiment_nb, sentiment_nb_acc, _ = train_model(
        MultinomialNB(alpha=0.1),
        "Sentiment Naive Bayes",
        X_train_s,
        X_test_s,
        y_train_s,
        y_test_s
    )
    sentiment_dt, sentiment_dt_acc, _ = train_model(
        DecisionTreeClassifier(random_state=42),
        "Sentiment Decision Tree",
        X_train_s,
        X_test_s,
        y_train_s,
        y_test_s
    )
    sentiment_rf, sentiment_rf_acc, _ = train_model(
        RandomForestClassifier(
        n_estimators=500,
        
        max_depth=None,
        
        min_samples_leaf=2,
        
        n_jobs=-1,
        
        random_state=42
        ),
        "Sentiment Random Forest",
        X_train_s,
        X_test_s,
        y_train_s,
        y_test_s
    )
    sentiment_svm, sentiment_svm_acc, _ = train_model(
        best_sentiment_svm,
        "Sentiment Linear SVM",
        X_train_s,
        X_test_s,
        y_train_s,
        y_test_s
    )
    # ==========================================================
    # THEME MODELS
    # ==========================================================
    theme_lr, theme_lr_acc, _ = train_model(
        best_theme_lr,
        "Theme Logistic Regression",
        X_train_t,
        X_test_t,
        y_train_t,
        y_test_t
    )
    theme_nb, theme_nb_acc, _ = train_model(
        MultinomialNB(alpha=0.1),
        "Theme Naive Bayes",
        X_train_t,
        X_test_t,
        y_train_t,
        y_test_t
    )
    theme_dt, theme_dt_acc, _ = train_model(
        DecisionTreeClassifier(random_state=42),
        "Theme Decision Tree",
        X_train_t,
        X_test_t,
        y_train_t,
        y_test_t
    )
    theme_rf, theme_rf_acc, _ = train_model(
        RandomForestClassifier(
            n_estimators=500,
            max_depth=None,
            min_samples_leaf=2,
            n_jobs=-1,
            random_state=42
        ),
        "Theme Random Forest",
        X_train_t,
        X_test_t,
        y_train_t,
        y_test_t
    )
    theme_svm, theme_svm_acc, _ = train_model(
        best_theme_svm,
        "Theme Linear SVM",
        X_train_t,
        X_test_t,
        y_train_t,
        y_test_t
    )
    # ==========================================================
    # SAVE MODELS
    # ==========================================================
    save_model(tfidf, "tfidf.pkl")
    save_model(selector_s, "selector_sentiment.pkl")
    save_model(selector_t, "selector_theme.pkl")
    save_model(sentiment_lr, "sentiment_lr.pkl")
    save_model(sentiment_nb, "sentiment_nb.pkl")
    save_model(sentiment_dt, "sentiment_dt.pkl")
    save_model(sentiment_rf, "sentiment_rf.pkl")
    save_model(sentiment_svm, "sentiment_svm.pkl")
    save_model(theme_lr, "theme_lr.pkl")
    save_model(theme_nb, "theme_nb.pkl")
    save_model(theme_dt, "theme_dt.pkl")
    save_model(theme_rf, "theme_rf.pkl")
    save_model(theme_svm, "theme_svm.pkl")
    # ==========================================================
    # RESULTS
    # ==========================================================
    print("\n" + "=" * 60)
    print("MODEL COMPARISON")
    print("=" * 60)
    print("\nSentiment Models")
    print(f"Logistic Regression : {sentiment_lr_acc:.4f}")
    print(f"Naive Bayes         : {sentiment_nb_acc:.4f}")
    print(f"Decision Tree       : {sentiment_dt_acc:.4f}")
    print(f"Random Forest       : {sentiment_rf_acc:.4f}")
    print(f"Linear SVM          : {sentiment_svm_acc:.4f}")
    print("\nTheme Models")
    print(f"Logistic Regression : {theme_lr_acc:.4f}")
    print(f"Naive Bayes         : {theme_nb_acc:.4f}")
    print(f"Decision Tree       : {theme_dt_acc:.4f}")
    print(f"Random Forest       : {theme_rf_acc:.4f}")
    print(f"Linear SVM          : {theme_svm_acc:.4f}")
    print("\nTraining Completed Successfully!")

if __name__ == "__main__":
    main()