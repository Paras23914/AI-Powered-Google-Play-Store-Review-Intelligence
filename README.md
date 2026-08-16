# AI-Powered Google Play Store Review Intelligence

An end-to-end review analysis system for Google Play Store reviews using traditional machine learning, transformer-based classification, and Generative AI.

The system allows users to upload Google Play Store review data, process reviews through multiple analysis pipelines, classify sentiment and themes, explore statistics and visualizations, and generate additional insights using Qwen and Gemini.

---

## Overview

Google Play Store reviews contain valuable information about user experience, application quality, bugs, requested features, pricing, advertisements, performance, and other issues.

However, analyzing thousands of reviews manually is difficult.

This project provides an automated review intelligence pipeline that combines:

- Data preprocessing
- Traditional Machine Learning
- TF-IDF feature extraction
- Chi-square feature selection
- Linear SVM classification
- DeBERTa-based classification
- Generative AI analysis
- Interactive React visualization

The system supports analysis of both **sentiment** and **review themes**.

---

# Key Features

- Upload Google Play Store review CSV files
- Validate uploaded review data
- Clean and preprocess review text
- Remove unwanted text patterns such as URLs
- TF-IDF feature extraction
- Chi-square feature selection
- Traditional ML model training and comparison
- Linear SVM sentiment classification
- Linear SVM theme classification
- DeBERTa sentiment classification
- DeBERTa theme classification
- Qwen3 8B local LLM analysis through Ollama
- Gemini API-based analysis
- Sentiment distribution analysis
- Theme distribution analysis
- Rating distribution analysis
- Interactive charts
- Review-level prediction tables
- Representative feedback
- Model comparison
- Downloadable analysis results
- React-based dashboard
- FastAPI backend

---

# System Architecture

```text
                       CSV REVIEW DATA
                              │
                              ▼
                     ┌─────────────────┐
                     │ React Frontend  │
                     │   Vite + React  │
                     └────────┬────────┘
                              │
                         HTTP / REST
                              │
                              ▼
                     ┌─────────────────┐
                     │ FastAPI Backend │
                     └────────┬────────┘
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
      Traditional ML       DeBERTa       Generative AI
             │                │                │
             │                │          ┌─────┴─────┐
             │                │          │           │
             ▼                ▼          ▼           ▼
          TF-IDF          Sentiment    Qwen3       Gemini
             │             + Theme      8B           API
             ▼                │        Ollama
       Feature Selection      │
             │                │
             ▼                │
        Linear SVM            │
             │                │
             └────────┬───────┘
                      │
                      ▼
                Analysis Results
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
      Dashboard    Results     Download
          │           │           │
          └───────────┴───────────┘
````

---

# Project Structure

The public repository contains the main Python backend files and the React frontend.

```text
PROJECT/
│
├── main.py
├── model_manager.py
├── predict.py
├── preprocess_predict.py
├── preprocessing.py
├── statistics.py
├── utils.py
│
├── train.py
│
├── llm_labeler.py
├── llm_pipeline.py
├── gemini_pipeline.py
│
├── Review_Analyser/
│   │
│   ├── public/
│   │
│   ├── src/
│   │   │
│   │   ├── assets/
│   │   │
│   │   ├── components/
│   │   │   ├── Cards/
│   │   │   ├── Charts/
│   │   │   ├── Common/
│   │   │   ├── Dashboard/
│   │   │   ├── Download/
│   │   │   ├── Loading/
│   │   │   ├── Table/
│   │   │   └── Upload/
│   │   │
│   │   ├── pages/
│   │   │
│   │   ├── services/
│   │   │
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

The following project assets are intentionally excluded from the public repository:

* Original datasets
* Processed datasets
* Labelled datasets
* Trained model artifacts
* DeBERTa model weights
* Local caches
* Generated result collections
* API keys and credentials

---

# Technology Stack

## Backend

* Python
* FastAPI
* Pandas
* NumPy
* scikit-learn
* PyTorch
* Hugging Face Transformers
* Joblib
* NLTK

## Machine Learning

* TF-IDF
* Chi-square feature selection
* Logistic Regression
* Naive Bayes
* Decision Tree
* Random Forest
* Linear SVM

## Transformer

* DeBERTa

## Generative AI

* Qwen3 8B
* Ollama
* Gemini API

## Frontend

* React
* Vite
* React Router
* Axios
* Recharts

---

# Input Data Format

The application accepts a CSV file containing review ratings and review text.

The minimum required columns are:

```csv
rating,content
5,"Amazing application!"
2,"The application keeps crashing."
4,"Good application but needs improvements."
```

The backend expects:

* `rating`
* `content`

The uploaded file is validated before analysis.

---

# Data Processing Pipeline

The overall processing flow is:

```text
Raw Review
     │
     ▼
CSV Validation
     │
     ▼
Text Preprocessing
     │
     ├────────────────────────────┐
     │                            │
     ▼                            ▼
ML Preprocessing             LLM / DeBERTa
     │                       Preprocessing
     ▼                            │
TF-IDF                            │
     │                            │
Chi-Square                        │
     │                            │
     ▼                            ▼
Linear SVM                     DeBERTa
     │                            │
     └──────────────┬─────────────┘
                    │
                    ▼
              Classification
                    │
                    ▼
          Generative AI Analysis
                    │
                    ▼
              Final Results
```

---

# Text Preprocessing

The project uses different preprocessing approaches depending on the analysis method.

## Traditional ML preprocessing

The traditional ML preprocessing prepares text for TF-IDF.

The processing includes:

* Lowercasing
* URL removal
* Punctuation handling
* Whitespace normalization
* Stopword removal
* Preservation of important negation words

Important negation words such as:

```text
not
no
never
```

are preserved because they can significantly affect sentiment.

---

## DeBERTa / LLM preprocessing

Transformer and LLM analysis uses lighter text cleaning so that more of the original natural-language structure is preserved.

The processing includes:

* URL removal
* Whitespace normalization
* Preservation of natural-language context

This prevents excessive preprocessing from removing information that transformer and generative models can use.

---

# Traditional Machine Learning

The traditional ML pipeline is used as a baseline and for comparison with the transformer approach.

```text
Review Text
     │
     ▼
Preprocessing
     │
     ▼
TF-IDF
     │
     ▼
Chi-Square Feature Selection
     │
     ▼
Traditional Classifiers
     │
     ├── Logistic Regression
     ├── Naive Bayes
     ├── Decision Tree
     ├── Random Forest
     └── Linear SVM
```

The models are evaluated using the same processed feature representation.

---

# TF-IDF

TF-IDF stands for:

**Term Frequency-Inverse Document Frequency**

It converts text into numerical features.

A term receives a higher value when:

* it occurs frequently in a particular document
* but is relatively uncommon across the complete collection

The project uses TF-IDF to convert review text into numerical vectors before traditional classification.

---

# Chi-Square Feature Selection

Chi-square feature selection is used to identify features that have a strong relationship with the target class.

The purpose is to:

* reduce the feature space
* remove less informative features
* improve computational efficiency
* retain features that are more useful for classification

The selected features are then passed to the traditional classifiers.

---

# Traditional Models

The project compares several traditional classification algorithms:

### 1. Logistic Regression

A linear classification algorithm commonly used for text classification.

### 2. Naive Bayes

A probabilistic classifier based on Bayes' theorem and the assumption of conditional independence between features.

### 3. Decision Tree

A tree-based classifier that recursively divides data according to feature conditions.

### 4. Random Forest

An ensemble of multiple decision trees.

### 5. Linear SVM

A Support Vector Machine using a linear decision boundary.

Linear SVM produced the strongest traditional baseline in the project and was selected as the primary traditional model.

---

# Linear SVM

Linear SVM is particularly suitable for high-dimensional sparse text representations such as TF-IDF.

The model attempts to find a decision boundary that separates different classes while maximizing the margin between them.

The project uses separate trained models for:

* Sentiment
* Theme

---

# DeBERTa

The project uses DeBERTa as the transformer-based classification approach.

Separate models are used for:

* Sentiment classification
* Theme classification

The DeBERTa pipeline works directly with tokenized review text rather than TF-IDF vectors.

```text
Review
   │
   ▼
Tokenizer
   │
   ▼
DeBERTa
   │
   ├─────────────┐
   ▼             ▼
Sentiment      Theme
Prediction     Prediction
```

The prediction pipeline processes reviews in batches.

The current implementation uses:

```text
Batch Size: 64
Maximum Sequence Length: 256
```

GPU acceleration is used when CUDA is available.

---

# Model Comparison

The project compared the selected traditional baseline against DeBERTa.

| Task      | Linear SVM Accuracy | DeBERTa Accuracy |
| --------- | ------------------: | ---------------: |
| Sentiment |              81.60% |           85.91% |
| Theme     |              69.56% |           75.32% |

DeBERTa produced higher observed accuracy on both tasks in the project evaluation.

### Accuracy Improvement

Sentiment:

```text
85.91% - 81.60%
= +4.31 percentage points
```

Theme:

```text
75.32% - 69.56%
= +5.76 percentage points
```

These are observed experimental differences on the project's evaluation set and should not be interpreted as statistically significant improvements because no statistical significance test was performed.

---

# Evaluation

The project evaluation set contained:

```text
2,342 reviews
```

The model-ready dataset contained:

```text
11,709 reviews
```

The split was:

```text
Training:    9,367
Evaluation:  2,342
Total:      11,709
```

---

# Sentiment Classes

The sentiment classification task contains three classes:

```text
Positive
Neutral
Negative
```

The model-ready dataset distribution was:

```text
Negative    6,141
Positive    4,468
Neutral     1,100
```

The distribution demonstrates class imbalance, particularly between Neutral and the other sentiment classes.

---

# Theme Classification

The project uses a 13-theme classification schema for the main classification task.

The themes include:

```text
General Praise
Bug Report
Feature Request
UI Problem
Other
Pricing Complaint
Customer Support
Ads Complaint
Login Problem
Performance Issue
Crash
Subscription Issue
Security Concern
Data Loss
```

The exact project data also contained rare/variant theme labels during the earlier labelling stage. These were handled as part of the project's data preparation and modelling process.

---

# Error Analysis

Overall accuracy alone does not fully describe model performance.

The project therefore examined class-level performance and the distribution of classes.

An important observation was that the Neutral sentiment class was more difficult to classify.

For the evaluation set:

```text
Actual Neutral reviews:       220
Correctly classified Neutral: 62
Neutral F1:                   34.54%
```

Theme classification also showed a difference between macro and weighted F1.

```text
Theme Macro F1:     53.87%
Theme Weighted F1: 73.89%
```

This indicates that larger classes contribute much more strongly to the weighted score, while minority classes can have considerably weaker performance.

---

# Generative AI Analysis

The project includes Generative AI as an additional analysis layer.

Two approaches are implemented:

```text
Qwen3 8B
Gemini
```

Generative AI is not simply used as a replacement for the classification models.

It provides additional natural-language analysis of reviews.

---

# Qwen3 8B

Qwen3 8B is used locally through Ollama.

The project configuration uses:

```text
Model: qwen3:8b
Batch Size: 32
Maximum Concurrent Requests: 2
```

The model generates structured information including:

* Review summary
* Sentiment
* Theme
* Short reasoning

The generated outputs are validated against the allowed sentiment and theme categories.

---

# Gemini

Gemini is used through the Google GenAI API.

The Gemini pipeline uses an API key supplied through an environment variable.

The required environment variable is:

```text
GEMINI_API_KEY
```

Example:

```text
GEMINI_API_KEY=your_api_key_here
```

Never commit the real API key to GitHub.

---

# Qwen and Gemini Runtime

During the project's demonstration/testing:

| Model    | Approximate Runtime |
| -------- | ------------------: |
| Qwen3 8B |        ~184 seconds |
| Gemini   |      ~11.88 seconds |

These measurements were obtained on the demonstration dataset used during the project.

They are **not general performance benchmarks** because runtime depends on:

* hardware
* network conditions
* model configuration
* number of reviews
* API/service availability
* local Ollama performance

Runtime should therefore be interpreted only in the context of the project's experiment.

---

# LLM Evaluation Note

LLM agreement should not automatically be interpreted as model accuracy.

The LLM-generated labels were not evaluated against a fully human-annotated gold-standard dataset.

Therefore:

```text
LLM Agreement ≠ Ground-Truth Accuracy
```

This is an important limitation of the project.

---

# React Web Application

The project contains a React-based frontend named:

```text
Review_Analyser
```

The frontend provides an interactive interface for the review analysis pipeline.

---

# Frontend Features

The application includes:

### Home

Provides the starting point for the review analysis workflow.

### Upload

Allows users to select and upload a CSV file.

### Dashboard

Displays:

* Total reviews
* Positive reviews
* Neutral reviews
* Negative reviews
* Average rating
* Rating distribution
* Sentiment distribution
* Theme distribution

### Results

Displays review-level predictions and analysis results.

### Analysis

Provides additional analytical views.

### LLM Selection

Allows users to select the available Generative AI analysis method.

### Gemini Analysis

Displays Gemini-based analysis.

### Qwen Analysis

Displays Qwen-based analysis.

### Download

Allows users to download generated analysis results.

---

# Frontend Components

The React application is organized into reusable components.

```text
src/
│
├── assets/
│
├── components/
│   │
│   ├── Cards/
│   │   ├── StatsCards.jsx
│   │   └── StatsCards.css
│   │
│   ├── Charts/
│   │   ├── RatingDistribution.jsx
│   │   ├── SentimentChart.jsx
│   │   ├── ThemeChart.jsx
│   │   └── Charts.css
│   │
│   ├── Common/
│   │   ├── Badge.jsx
│   │   ├── InfoCard.jsx
│   │   ├── SectionCard.jsx
│   │   └── ThemeToggle.jsx
│   │
│   ├── Dashboard/
│   │   ├── Dashboard.jsx
│   │   ├── ComparisonSection.jsx
│   │   ├── ModelSelection.jsx
│   │   ├── PriorityIssues.jsx
│   │   └── RepresentativeFeedback.jsx
│   │
│   ├── Download/
│   │   └── DownloadButton.jsx
│   │
│   ├── Loading/
│   │   └── LoadingScreen.jsx
│   │
│   ├── Table/
│   │   └── PredictionTable.jsx
│   │
│   └── Upload/
│       └── UploadSection.jsx
│
├── pages/
│
├── services/
│   └── api.js
│
├── App.jsx
├── App.css
├── index.css
└── main.jsx
```

---

# Backend Files

## `main.py`

The main FastAPI application.

It handles the API endpoints and connects the frontend with the analysis pipelines.

Start the backend using:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

---

## `model_manager.py`

Responsible for loading the trained machine-learning and DeBERTa models.

It also determines whether inference should use:

```text
CUDA GPU
```

or:

```text
CPU
```

The trained model artifacts themselves are not included in this public repository.

---

## `predict.py`

Responsible for prediction using the trained models.

It connects preprocessing, traditional ML models and DeBERTa prediction.

---

## `preprocess_predict.py`

Provides preprocessing used during model prediction.

It contains the ML and lighter text-cleaning approaches required by the different model pipelines.

---

## `preprocessing.py`

Contains the main preprocessing functionality used during model development/training.

---

## `statistics.py`

Generates statistical summaries from the review analysis results, including:

* sentiment distribution
* theme distribution
* rating distribution
* average rating
* priority/issue-related information

---

## `train.py`

Contains the traditional machine-learning training and model-comparison pipeline.

It can be used to train and compare:

* Logistic Regression
* Naive Bayes
* Decision Tree
* Random Forest
* Linear SVM

Training generates the model artifacts required by the inference pipeline.

**Training is not required every time the application is started.**

---

## `llm_labeler.py`

Provides the LLM-assisted labelling functionality used during the project.

---

## `llm_pipeline.py`

Provides the local Qwen/Ollama analysis pipeline.

---

## `gemini_pipeline.py`

Provides Gemini-based analysis through the Google GenAI API.

---

## `utils.py`

Contains shared utility functionality used by the backend.

---

# Running the Project

The project consists of two applications:

```text
Backend  → FastAPI
Frontend → React + Vite
```

Both applications need to be running simultaneously.

---

# Prerequisites

Install the following before running the project:

* Python 3.10+
* Node.js
* npm
* Git

For Qwen analysis:

* Ollama
* Qwen3 8B model

For Gemini analysis:

* Google Gemini API access
* Gemini API key

For GPU acceleration:

* CUDA-compatible NVIDIA GPU
* Compatible PyTorch CUDA installation

---

# Backend Setup

Open a terminal in the project root where `main.py` is located.

## 1. Create a virtual environment

### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 2. Install Python Dependencies

Install the required packages:

```bash
pip install fastapi uvicorn pandas numpy scikit-learn joblib torch transformers nltk pydantic python-multipart
```

For Gemini:

```bash
pip install google-genai
```

For Ollama:

```bash
pip install ollama
```

---

# NLTK Setup

The preprocessing pipeline uses NLTK stopwords.

If required, run:

```python
import nltk
nltk.download("stopwords")
```

---

# Model Files

The public GitHub repository does not contain the trained model files.

The original project expects trained artifacts in locations such as:

```text
Models/
deberta_models/
```

These directories are intentionally excluded from the public repository.

The application therefore requires the appropriate trained artifacts to be supplied separately if full model inference is required.

---

# Gemini Setup

Set the Gemini API key as an environment variable.

### Windows PowerShell

```powershell
$env:GEMINI_API_KEY="YOUR_API_KEY"
```

### Windows Command Prompt

```cmd
set GEMINI_API_KEY=YOUR_API_KEY
```

### macOS / Linux

```bash
export GEMINI_API_KEY="YOUR_API_KEY"
```

Do not commit your API key.

---

# Qwen / Ollama Setup

Install Ollama and ensure the Ollama service is running.

The project expects the Qwen model:

```text
qwen3:8b
```

Make sure the model is available locally before selecting Qwen analysis in the application.

---

# Start the Backend

From the project root:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The FastAPI backend will run at:

```text
http://127.0.0.1:8000
```

FastAPI documentation will be available at:

```text
http://127.0.0.1:8000/docs
```

---

# Start the Frontend

Open a **second terminal**.

Navigate into the React application:

```bash
cd Review_Analyser
```

Install dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

# Correct Startup Order

Use the following order when running the complete application:

```text
1. Start Ollama
      │
      │
      │   Required only for Qwen
      ▼
2. Start FastAPI Backend
      │
      ▼
3. Start React/Vite Frontend
      │
      ▼
4. Open the application
      │
      ▼
5. Upload CSV
      │
      ▼
6. Select analysis
      │
      ▼
7. Process reviews
      │
      ▼
8. View dashboard/results
      │
      ▼
9. Download results
```

If Qwen is not being used, Ollama is not required for the traditional ML/DeBERTa/Gemini workflow.

---

# Important: Do Not Run Every Python File

The Python files are connected through imports.

You normally **do not** run these individually:

```text
model_manager.py
predict.py
preprocessing.py
preprocess_predict.py
statistics.py
llm_pipeline.py
gemini_pipeline.py
utils.py
```

The main backend entry point is:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

`train.py` is different because it is used for model training and comparison rather than normal application startup.

---

# Training Workflow

If you have the original training data and want to retrain the traditional models:

```text
Training Data
     │
     ▼
Preprocessing
     │
     ▼
TF-IDF
     │
     ▼
Chi-Square Selection
     │
     ▼
Model Training
     │
     ├── Logistic Regression
     ├── Naive Bayes
     ├── Decision Tree
     ├── Random Forest
     └── Linear SVM
     │
     ▼
Saved Model Artifacts
```

Run:

```bash
python train.py
```

The trained artifacts are then used by the prediction pipeline.

**Do not run `train.py` just to start the web application.**

---

# Prediction Workflow

Normal application inference follows:

```text
CSV Upload
    │
    ▼
main.py
    │
    ▼
Prediction Pipeline
    │
    ├── Traditional ML
    │
    └── DeBERTa
    │
    ▼
Statistics
    │
    ▼
Frontend
```

---

# API Communication

The React frontend communicates with the FastAPI backend using HTTP requests.

The frontend API configuration uses:

```text
http://127.0.0.1:8000
```

The backend receives uploaded files and returns analysis information to the frontend.

---

# Example CSV

A minimal test file can be created as:

```csv
rating,content
5,"Amazing application and very easy to use."
2,"The application keeps crashing."
3,"It is okay but needs improvement."
1,"There are too many advertisements."
4,"Good application but login is sometimes slow."
5,"Excellent experience!"
2,"The latest update introduced bugs."
3,"The application is fine."
```

Save it as:

```text
sample_reviews.csv
```

Then upload it through the web application.

---

# Results

The application can produce:

* Review-level sentiment predictions
* Review-level theme predictions
* Rating statistics
* Sentiment statistics
* Theme statistics
* Representative feedback
* Model comparison information
* Generative AI analysis
* Downloadable result files

---

# Project Dataset

The original project dataset is intentionally **not included** in this repository.

During project development, the working dataset contained:

```text
Original reviews:              12,495
Exact duplicate rows removed:    688
After duplicate removal:      11,807
Rows removed during ML cleaning: 98
Final model-ready reviews:    11,709
```

The model-ready data was split into:

```text
Training:     9,367
Evaluation:   2,342
Total:       11,709
```

The original and processed datasets are excluded from the public GitHub repository.

---

# Model Results

The selected traditional baseline was Linear SVM.

The project evaluation produced:

| Task                  | Linear SVM |    DeBERTa |
| --------------------- | ---------: | ---------: |
| Sentiment Accuracy    |     81.60% | **85.91%** |
| Theme Accuracy        |     69.56% | **75.32%** |
| Sentiment Weighted F1 |     80.35% | **84.99%** |
| Theme Weighted F1     |     69.39% | **73.89%** |

DeBERTa achieved higher observed performance on both sentiment and theme classification.

---

# Model Performance Interpretation

The results should not be interpreted using accuracy alone.

The dataset contains class imbalance, especially for themes.

For example:

```text
Theme Macro F1:     53.87%
Theme Weighted F1: 73.89%
```

The difference indicates that the model performs considerably better on the larger classes than on some minority classes.

Similarly, Neutral sentiment was more difficult to classify.

Therefore, the project considers:

* Accuracy
* Precision
* Recall
* F1-score
* Macro F1
* Weighted F1
* Class distributions
* Error analysis

rather than relying on a single metric.

---

# Limitations

The project has several limitations.

### 1. AI-Assisted Labelling

The sentiment and theme labels used during development were generated with AI assistance.

They were not validated against a completely human-annotated gold-standard dataset.

Therefore, label quality can affect downstream model performance.

### 2. Class Imbalance

Some themes have significantly fewer examples than the major classes.

This can result in poor minority-class performance.

### 3. Neutral Sentiment

Neutral reviews are more difficult for the classifier to distinguish from positive and negative reviews.

### 4. LLM Agreement

Agreement between LLM outputs should not be considered equivalent to ground-truth accuracy.

### 5. Runtime

Qwen and Gemini runtime measurements depend on the local hardware, API conditions, model configuration, and dataset size.

### 6. Statistical Significance

The project did not perform statistical significance testing for the difference between Linear SVM and DeBERTa.

Therefore, the reported improvements are observed experimental differences.

---

# Future Improvements

Potential future improvements include:

* Human validation of generated labels
* Creation of a human-annotated gold-standard dataset
* Better class balancing
* Additional minority-class handling
* Hyperparameter optimization
* Statistical significance testing
* Larger evaluation datasets
* More comprehensive LLM benchmarking
* Database-backed result storage
* User authentication
* Production deployment
* More robust monitoring and logging

---

# Security

Never commit:

```text
.env
API keys
credentials
private datasets
trained model weights
private configuration files
```

The Gemini API key must be supplied through an environment variable:

```text
GEMINI_API_KEY
```

The `.gitignore` file is configured to prevent sensitive and large project artifacts from being committed accidentally.

---

# Development Notes

This repository is the cleaned public version of the academic project.

The original development environment contained additional:

* datasets
* trained models
* experiment outputs
* temporary scripts
* caches
* debugging files

These are intentionally not included in the public repository.

The goal of this repository is to present the main implementation and architecture clearly while avoiding unnecessary large or private artifacts.

---

# Academic Context

This project was developed as an academic Data Mining project.

The project combines concepts from:

* Data preprocessing
* Text mining
* Feature extraction
* Feature selection
* Classification
* Machine learning
* Transformer-based NLP
* Model evaluation
* Error analysis
* Generative AI
* Web application development

---

## Authors

### Paras Sharma
Project Lead & ML/Full-Stack Developer

- Data preprocessing & analysis
- Machine Learning & DeBERTa pipeline
- Qwen & Gemini integration
- FastAPI backend
- React dashboard
- Model evaluation

### Devam Dharmendrabhai Shah
Frontend Developer

- React frontend
- Dashboard UI
- Data visualization
- UI components

Academic Data Mining Project.

---

# License

This repository is provided for academic and portfolio purposes.

Please contact the authors before redistributing substantial portions of the implementation or using the project commercially.

