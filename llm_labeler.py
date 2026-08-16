import pandas as pd
import ollama
import json

# ==========================================================
# CONFIGURATION
# ==========================================================

INPUT_FILE = "data/clean_reviews.csv"
MODEL_NAME = "gemma3:4b"
OUTPUT_FILE = "data/labelled_reviews.csv"

def load_dataset():
    """
    Load the cleaned review dataset.
    """

    print("=" * 60)
    print("Loading Clean Dataset...")
    print("=" * 60)

    df = pd.read_csv(INPUT_FILE)

    print(f"\nTotal Reviews : {len(df)}")

    return df

def build_prompt(review):

    return f"""
You are an expert software engineer specializing in Google Play Store review analysis.

Your task is to classify ONE review.

Review:
{review}

IMPORTANT RULES

1. Ignore the rating completely.
2. Analyze ONLY the review text.
3. Return ONLY valid JSON.
4. Do NOT use markdown.
5. Do NOT explain your reasoning.
6. Choose the MOST SPECIFIC theme possible.
7. Use "Bug Report" ONLY if no specific category fits.

Sentiment must be EXACTLY one of:

- Positive
- Neutral
- Negative

Theme Definitions

1. Crash
- App crashes
- Force closes
- Closes unexpectedly
- Won't open after launch

2. Login Problem
- Cannot login
- Authentication failed
- OTP issues
- Password issues
- Sign in problems

3. Performance Issue
- Slow
- Lag
- Freezing
- High battery usage
- High memory usage
- Long loading time

4. UI Problem
- Buttons not working
- Layout issues
- Display problems
- Navigation issues
- Visual glitches

5. Customer Support
- No response
- Refund issue
- Poor customer service

6. Pricing Complaint
- Too expensive
- Costly subscription
- Poor value

7. Subscription Issue
- Premium not activated
- Subscription cancelled
- Payment issue

8. Ads Complaint
- Too many ads
- Intrusive advertisements

9. Feature Request
- Requests a new feature
- Suggests improvements

10. Security Concern
- Privacy issue
- Data leak
- Security vulnerability

11. General Praise
- Mainly compliments the app

12. Bug Report
- A software defect that does NOT clearly belong to Crash,
  Login Problem, Performance Issue, UI Problem,
  Security Concern, Subscription Issue,
  Customer Support, Pricing Complaint,
  Ads Complaint or Feature Request.

13. Other
- Use ONLY if none of the above categories apply.

Priority Rules

If multiple themes appear, ALWAYS choose the most specific one.

Priority order:

Crash
→ Login Problem
→ Performance Issue
→ Subscription Issue
→ Security Concern
→ UI Problem
→ Customer Support
→ Pricing Complaint
→ Ads Complaint
→ Feature Request
→ General Praise
→ Bug Report
→ Other

Examples

Review:
"The app crashes every time I open it."

{{
    "sentiment":"Negative",
    "theme":"Crash"
}}

Review:
"I can't sign in after the latest update."

{{
    "sentiment":"Negative",
    "theme":"Login Problem"
}}

Review:
"The app is extremely slow and freezes."

{{
    "sentiment":"Negative",
    "theme":"Performance Issue"
}}

Review:
"The app has a bug where notifications don't work."

{{
    "sentiment":"Negative",
    "theme":"Bug Report"
}}

Return ONLY this JSON:

{{
    "sentiment":"Positive",
    "theme":"General Praise"
}}

FINAL DECISION RULES

1. Always choose the MOST SPECIFIC applicable theme.
2. Bug Report is the LAST RESORT category.
3. If the review explicitly mentions crashing, force closing or not opening → Crash.
4. If the review explicitly mentions login, OTP, authentication or password → Login Problem.
5. If the review explicitly mentions lag, freezing, slow performance or loading forever → Performance Issue.
6. If multiple themes are possible, select the MOST SPECIFIC one.
If a review contains both a general bug description and a more specific issue,
ALWAYS choose the more specific theme.
"""

def classify_review(review):

    prompt = build_prompt(review)

    response = ollama.chat(

        model=MODEL_NAME,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]

    )

    return response["message"]["content"]

def clean_response(reply):

    reply = reply.strip()

    reply = reply.replace("```json", "")
    reply = reply.replace("```", "")

    return reply.strip()

def parse_response(reply):

    try:

        reply = clean_response(reply)

        result = json.loads(reply)

        sentiment = result["sentiment"]
        theme = result["theme"]

        return sentiment, theme

    except Exception:

        return None, None

def validate_prediction(score, sentiment):

    if score == 5 and sentiment == "Negative":
        return "Review"

    elif score <= 2 and sentiment == "Positive":
        return "Review"

    else:
        return "OK"

def save_result(results, output_file):

    df = pd.DataFrame(results)

    df.to_csv(output_file, index=False)

df = load_dataset()
results = []
for index, row in df.iterrows():

    review = row["clean_content_llm"]

    score = row["score"]

    reply = classify_review(review)

    sentiment, theme = parse_response(reply)

    validation = validate_prediction(score, sentiment)
    print(f"{index+1}/{len(df)} Processed")

    results.append({

    "content": row["content"],

    "score": score,

    "clean_content_ml": row["clean_content_ml"],

    "clean_content_llm": review,

    "sentiment": sentiment,

    "theme": theme,

    "validation": validation,

    "llm_model": MODEL_NAME

    })

save_result(results, OUTPUT_FILE)

print("\nDataset saved successfully!")
