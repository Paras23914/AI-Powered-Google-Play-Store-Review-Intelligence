import json
import time
import ollama
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed


# ==========================================================
# CONFIGURATION
# ==========================================================

MODEL_NAME = "qwen3:8b"

# Tested reliable configuration
LLM_BATCH_SIZE = 32
MAX_CONCURRENT_REQUESTS = 2

# Faster Qwen3 mode
LLM_THINKING = False

# Retry failed batches before splitting
MAX_RETRIES = 2


# ==========================================================
# ALLOWED VALUES
# ==========================================================

ALLOWED_SENTIMENTS = {
    "Positive",
    "Neutral",
    "Negative"
}

ALLOWED_THEMES = {
    "Crash",
    "Login Problem",
    "Performance Issue",
    "UI Problem",
    "Customer Support",
    "Pricing Complaint",
    "Subscription Issue",
    "Ads Complaint",
    "Feature Request",
    "Security Concern",
    "General Praise",
    "Bug Report",
    "Other"
}


# ==========================================================
# PROMPT
# ==========================================================

def build_batch_prompt(reviews):

    review_text = "\n\n".join(
        f"Review {i + 1}:\n{review}"
        for i, review in enumerate(reviews)
    )

    return f"""
You are an expert in Google Play Store review analysis.

Analyze every review independently.

{review_text}

For EACH review determine:

1. A short factual summary.
2. Sentiment.
3. Exactly ONE theme.
4. A short reason.

Sentiment MUST be exactly one of:

Positive
Neutral
Negative

Theme MUST be exactly one of:

Crash
Login Problem
Performance Issue
UI Problem
Customer Support
Pricing Complaint
Subscription Issue
Ads Complaint
Feature Request
Security Concern
General Praise
Bug Report
Other

RULES:

- Analyze ONLY the review text.
- The rating is provided separately and must NOT be used
  to determine sentiment.
- Choose exactly ONE theme.
- Choose the MOST SPECIFIC applicable theme.
- Do not infer an issue that is not explicitly supported.
- If the app crashes, force closes, or cannot open, use Crash.
- If the issue is login, OTP, authentication, or password,
  use Login Problem.
- If the issue explicitly describes slow performance, lag,
  freezing, or loading, use Performance Issue.
- Use UI Problem for interface, layout, button, navigation,
  display, or visual problems.
- Use Customer Support for support, refund, or contact
  response issues.
- Use Pricing Complaint for cost or value complaints.
- Use Subscription Issue for subscription, payment activation,
  renewal, or cancellation issues.
- Use Ads Complaint for advertising complaints.
- Use Security Concern for privacy, security, or data concerns.
- Use Feature Request when the user requests a feature
  or improvement.
- Use General Praise when the review is mainly positive praise.
- Use Bug Report for an explicit software defect that does not
  clearly fit a more specific category.
- Use Other when no category applies.
- Never invent a theme.
- Do not provide chain-of-thought.
- Keep summaries very short.
- Keep reasons very short.
- Summary should normally be 8 words or fewer.
- Reason should normally be 8 words or fewer.

IMPORTANT:

Return exactly ONE result for every review.

IDs MUST match the review numbers.

Return ONLY valid JSON.

Required structure:

{{
    "results": [
        {{
            "id": 1,
            "summary": "Cannot open application",
            "sentiment": "Negative",
            "theme": "Crash",
            "reason": "Application fails to open"
        }}
    ]
}}

The number of results MUST equal the number of reviews.
"""


# ==========================================================
# OLLAMA REQUEST
# ==========================================================

def request_batch(reviews):

    prompt = build_batch_prompt(reviews)

    response = ollama.chat(
        model=MODEL_NAME,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        format="json",

        think=LLM_THINKING,

        options={
            "temperature": 0
        }
    )

    reply = response["message"]["content"].strip()

    reply = reply.replace("```json", "")
    reply = reply.replace("```", "")
    reply = reply.strip()

    try:

        return json.loads(reply)

    except json.JSONDecodeError:

        return None


# ==========================================================
# VALIDATE ONE RESULT
# ==========================================================

def validate_result(result, expected_id):

    if not isinstance(result, dict):
        return False

    if result.get("id") != expected_id:
        return False

    if not isinstance(result.get("summary"), str):
        return False

    if not isinstance(result.get("sentiment"), str):
        return False

    if not isinstance(result.get("theme"), str):
        return False

    if not isinstance(result.get("reason"), str):
        return False

    if result["sentiment"] not in ALLOWED_SENTIMENTS:
        return False

    if result["theme"] not in ALLOWED_THEMES:
        return False

    return True


# ==========================================================
# VALIDATE BATCH
# ==========================================================

def validate_batch(data, expected_count):

    if not isinstance(data, dict):
        return False, None

    results = data.get("results")

    if not isinstance(results, list):
        return False, None

    if len(results) != expected_count:
        return False, None

    expected_ids = set(
        range(1, expected_count + 1)
    )

    received_ids = set()

    for result in results:

        if not isinstance(result, dict):
            return False, None

        result_id = result.get("id")

        if result_id in received_ids:
            return False, None

        received_ids.add(result_id)

    if received_ids != expected_ids:
        return False, None

    for result in results:

        if not validate_result(
            result,
            result["id"]
        ):
            return False, None

    results.sort(
        key=lambda x: x["id"]
    )

    return True, results


# ==========================================================
# PROCESS ONE BATCH
# ==========================================================

def process_batch(reviews):

    expected_count = len(reviews)

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        print(
            f"    Attempt {attempt}/{MAX_RETRIES}",
            flush=True
        )

        data = request_batch(reviews)

        valid, results = validate_batch(
            data,
            expected_count
        )

        if valid:

            print(
                "    ✓ Batch validated",
                flush=True
            )

            return results

        print(
            "    ⚠ Invalid batch response",
            flush=True
        )

    # ------------------------------------------------------
    # Split failed batch
    # ------------------------------------------------------

    if len(reviews) == 1:

        print(
            "    ✗ Single review failed",
            flush=True
        )

        return [
            {
                "id": 1,
                "summary": None,
                "sentiment": None,
                "theme": None,
                "reason": None
            }
        ]

    midpoint = len(reviews) // 2

    left_reviews = reviews[:midpoint]
    right_reviews = reviews[midpoint:]

    print(
        f"    ↳ Splitting "
        f"{len(reviews)} → "
        f"{len(left_reviews)} + "
        f"{len(right_reviews)}",
        flush=True
    )

    left_results = process_batch(
        left_reviews
    )

    right_results = process_batch(
        right_reviews
    )

    # Rebuild local IDs

    for index, result in enumerate(
        left_results
    ):

        result["id"] = index + 1

    for index, result in enumerate(
        right_results
    ):

        result["id"] = (
            len(left_results)
            + index
            + 1
        )

    return left_results + right_results


# ==========================================================
# WORKER
# ==========================================================

def process_batch_worker(
    batch_number,
    start,
    batch
):

    print(
        f"\n[Worker] Batch {batch_number}"
        f" | Reviews {start + 1}-"
        f"{start + len(batch)}",
        flush=True
    )

    batch_start = time.perf_counter()

    results = process_batch(
        batch
    )

    batch_time = (
        time.perf_counter()
        - batch_start
    )

    # Convert local IDs to global IDs

    for result in results:

        result["id"] += start

    speed = (
        len(batch) / batch_time
        if batch_time > 0
        else 0
    )

    print(
        f"[Worker] Batch {batch_number} "
        f"completed in {batch_time:.2f}s "
        f"| {speed:.2f} reviews/sec",
        flush=True
    )

    return (
        batch_number,
        results,
        batch_time
    )


# ==========================================================
# PRODUCTION QWEN PIPELINE
# ==========================================================

def predict_llm(
    df: pd.DataFrame,
    progress_callback=None
):

    print("=" * 60)
    print("Qwen3 8B Parallel LLM Pipeline")
    print("=" * 60)

    print(
        f"Model          : {MODEL_NAME}"
    )

    print(
        f"Batch Size     : {LLM_BATCH_SIZE}"
    )

    print(
        f"Thinking       : {LLM_THINKING}"
    )

    print(
        f"Parallel Workers: "
        f"{MAX_CONCURRENT_REQUESTS}"
    )

    start_time = time.perf_counter()

    # ======================================================
    # INPUT VALIDATION
    # ======================================================

    if not isinstance(
        df,
        pd.DataFrame
    ):

        raise TypeError(
            "predict_llm() expects a pandas DataFrame."
        )

    if df.empty:

        raise ValueError(
            "Input CSV contains no records."
        )

    # ------------------------------------------------------
    # Required user columns
    # ------------------------------------------------------

    required_columns = {
        "rating",
        "content"
    }

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    if missing_columns:

        raise ValueError(
            "Missing required column(s): "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    # ------------------------------------------------------
    # Only these two input columns are required.
    # ------------------------------------------------------

    working_df = df[
        ["rating", "content"]
    ].copy()

    # ======================================================
    # PREPARE REVIEWS
    # ======================================================

    reviews = (
        working_df["content"]
        .fillna("")
        .astype(str)
        .tolist()
    )

    # Reject completely empty review content

    if all(
        not review.strip()
        for review in reviews
    ):

        raise ValueError(
            "Column 'content' contains no review text."
        )

    total = len(reviews)

    print(
        f"Reviews        : {total}"
    )

    # ======================================================
    # CREATE BATCHES
    # ======================================================

    batches = []

    for start in range(
        0,
        total,
        LLM_BATCH_SIZE
    ):

        end = min(
            start + LLM_BATCH_SIZE,
            total
        )

        batch_number = (
            start // LLM_BATCH_SIZE
        ) + 1

        batches.append(
            (
                batch_number,
                start,
                reviews[start:end]
            )
        )

    total_batches = len(batches)

    print(
        f"Total Batches  : {total_batches}"
    )

    # ======================================================
    # INITIAL PROGRESS
    # ======================================================

    if progress_callback:

        progress_callback({
            "status": "processing",
            "total_reviews": total,
            "total_batches": total_batches,
            "completed_batches": 0,
            "current_batch": None,
            "message": (
                f"Starting Qwen3 8B analysis "
                f"of {total} reviews"
            )
        })

    # ======================================================
    # PARALLEL EXECUTION
    # ======================================================

    completed_batches = {}

    with ThreadPoolExecutor(
        max_workers=MAX_CONCURRENT_REQUESTS
    ) as executor:

        futures = {
            executor.submit(
                process_batch_worker,
                batch_number,
                start,
                batch
            ): batch_number

            for batch_number, start, batch
            in batches
        }

        for future in as_completed(
            futures
        ):

            batch_number = futures[
                future
            ]

            try:

                (
                    returned_batch_number,
                    results,
                    batch_time
                ) = future.result()

                completed_batches[
                    returned_batch_number
                ] = results

                completed_count = len(
                    completed_batches
                )

                print(
                    f"✓ Completed "
                    f"{completed_count}/"
                    f"{total_batches} batches",
                    flush=True
                )

                # ------------------------------------------------
                # REAL FRONTEND PROGRESS
                # ------------------------------------------------

                if progress_callback:

                    progress_callback({

                        "status": "processing",

                        "total_reviews":
                            total,

                        "total_batches":
                            total_batches,

                        "completed_batches":
                            completed_count,

                        "current_batch":
                            returned_batch_number,

                        "message":
                            (
                                f"Batch "
                                f"{returned_batch_number}/"
                                f"{total_batches} completed"
                            )
                    })

            except Exception as e:

                print(
                    f"✗ Batch {batch_number} "
                    f"failed: {e}",
                    flush=True
                )

                if progress_callback:

                    progress_callback({

                        "status": "failed",

                        "total_reviews":
                            total,

                        "total_batches":
                            total_batches,

                        "completed_batches":
                            len(
                                completed_batches
                            ),

                        "current_batch":
                            batch_number,

                        "message":
                            (
                                f"Batch "
                                f"{batch_number} failed"
                            ),

                        "error":
                            str(e)
                    })

                raise

    # ======================================================
    # REASSEMBLE ORIGINAL ORDER
    # ======================================================

    all_results = []

    for batch_number in range(
        1,
        total_batches + 1
    ):

        if batch_number not in completed_batches:

            raise RuntimeError(
                f"Missing batch {batch_number}"
            )

        all_results.extend(
            completed_batches[
                batch_number
            ]
        )

    # ======================================================
    # FINAL VALIDATION
    # ======================================================

    if len(all_results) != total:

        raise RuntimeError(
            f"Expected {total} results "
            f"but received "
            f"{len(all_results)}."
        )

    all_results.sort(
        key=lambda x: x["id"]
    )

    expected_ids = list(
        range(
            1,
            total + 1
        )
    )

    received_ids = [
        result["id"]
        for result in all_results
    ]

    if received_ids != expected_ids:

        raise RuntimeError(
            "LLM result IDs do not match "
            "the input dataset."
        )

    # ======================================================
    # BUILD FINAL RESULT
    # ======================================================

    result_df = working_df.copy()

    result_df["llm_summary"] = [
        result["summary"]
        for result in all_results
    ]

    result_df["llm_sentiment"] = [
        result["sentiment"]
        for result in all_results
    ]

    result_df["llm_theme"] = [
        result["theme"]
        for result in all_results
    ]

    result_df["llm_reason"] = [
        result["reason"]
        for result in all_results
    ]

    # ======================================================
    # PERFORMANCE
    # ======================================================

    processing_time = round(
        time.perf_counter()
        - start_time,
        2
    )

    reviews_per_second = (
        total / processing_time
        if processing_time > 0
        else 0
    )

    print("\n" + "=" * 60)
    print("✓ Qwen3 8B COMPLETED")
    print("=" * 60)

    print(
        f"Total Reviews : {total}"
    )

    print(
        f"Workers       : "
        f"{MAX_CONCURRENT_REQUESTS}"
    )

    print(
        f"Batch Size    : "
        f"{LLM_BATCH_SIZE}"
    )

    print(
        f"Processing Time: "
        f"{processing_time}s"
    )

    print(
        f"Reviews/sec   : "
        f"{reviews_per_second:.2f}"
    )

    # ======================================================
    # FINAL PROGRESS
    # ======================================================

    if progress_callback:

        progress_callback({

            "status": "completed",

            "total_reviews":
                total,

            "total_batches":
                total_batches,

            "completed_batches":
                total_batches,

            "current_batch":
                total_batches,

            "message":
                "Qwen3 8B analysis completed",

            "processing_time":
                processing_time,

            "reviews_per_second":
                reviews_per_second
        })

    # ======================================================
    # STATISTICS FOR FASTAPI
    # ======================================================

    statistics = {

        "model":
            MODEL_NAME,

        "total_reviews":
            total,

        "batch_size":
            LLM_BATCH_SIZE,

        "parallel_workers":
            MAX_CONCURRENT_REQUESTS,

        "thinking":
            LLM_THINKING,

        "processing_time":
            processing_time,

        "reviews_per_second":
            reviews_per_second
    }

    return result_df, statistics