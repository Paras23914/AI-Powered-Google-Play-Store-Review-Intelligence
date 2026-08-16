import os
import json
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from google import genai
from pydantic import BaseModel


# ============================================================
# CONFIGURATION
# ============================================================

MODEL = "gemini-3.1-flash-lite"

BATCH_SIZE = 32
PARALLEL_WORKERS = 3

MAX_ATTEMPTS = 3

# Minimal is the tested configuration
THINKING_LEVEL = "minimal"


# ============================================================
# API KEY
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable not found."
    )

client = genai.Client(api_key=API_KEY)


# ============================================================
# STRUCTURED OUTPUT SCHEMA
# ============================================================

class ReviewResult(BaseModel):
    index: int
    llm_summary: str
    llm_sentiment: str
    llm_theme: str
    llm_reason: str


class BatchResult(BaseModel):
    results: list[ReviewResult]


# ============================================================
# PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are analyzing Google Play Store app reviews.

For every review, produce exactly:

1. llm_summary
   - Very short summary of the main point.
   - Usually 3-8 words.

2. llm_sentiment
   - Exactly one of:
     Positive
     Neutral
     Negative

3. llm_theme

Choose EXACTLY ONE theme from this list:

- Crash
- Login Problem
- Performance Issue
- UI Problem
- Customer Support
- Pricing Complaint
- Subscription Issue
- Ads Complaint
- Feature Request
- Security Concern
- General Praise
- Bug Report
- Other

Rules:

- NEVER create a new theme.
- ALWAYS choose exactly one theme from the list.
- Choose the MOST SPECIFIC applicable theme.
- If the app crashes or force closes, use Crash.
- If the main issue is login, OTP, authentication or password,
  use Login Problem.
- If the main issue is slowness, lag, freezing or loading,
  use Performance Issue.
- Use UI Problem for interface, layout, button, navigation,
  display, or visual problems.
- Use Customer Support for support, refund, or contact
  response issues.
- Use Pricing Complaint for cost or value complaints.
- Use Subscription Issue for subscription, payment,
  activation, renewal, or cancellation issues.
- Use Ads Complaint for advertising complaints.
- Use Security Concern for privacy, security, or data concerns.
- Use Feature Request when the user requests a feature
  or improvement.
- Use General Praise when the review is mainly positive praise.
- Use Bug Report only when no more specific category applies.
- Use Other only when none of the categories apply.

4. llm_reason
   - Short explanation of why the sentiment/theme was assigned.

Important:

- Analyze ONLY the review text.
- Do NOT use the numerical rating to determine sentiment.
- Do NOT invent information.
- If a review contains almost no meaningful information:
    sentiment = Neutral
    theme = Other
- Preserve the review index exactly.
- Return one result for every review.
"""


# ============================================================
# THREAD-SAFE PRINT
# ============================================================

print_lock = threading.Lock()


def log(message):

    with print_lock:
        print(message, flush=True)


# ============================================================
# PROCESS ONE BATCH
# ============================================================

def process_batch(batch_number, batch_df):

    start_time = time.time()

    indices = batch_df["__index"].tolist()

    reviews_text = []

    for _, row in batch_df.iterrows():

        reviews_text.append(
            f"REVIEW INDEX: {int(row['__index'])}\n"
            f"REVIEW: {str(row['content'])}"
        )

    prompt = SYSTEM_PROMPT + "\n\n"

    prompt += """
Analyze the following reviews.

Return exactly one result for every REVIEW INDEX.

REVIEWS:
"""

    prompt += "\n\n".join(
        reviews_text
    )

    for attempt in range(
        1,
        MAX_ATTEMPTS + 1
    ):

        log(
            f"[Worker] Batch {batch_number} | "
            f"Reviews {indices[0] + 1}-{indices[-1] + 1}"
        )

        log(
            f"Attempt {attempt}/{MAX_ATTEMPTS}"
        )

        try:

            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config={
                    "system_instruction":
                        SYSTEM_PROMPT,

                    "response_mime_type":
                        "application/json",

                    "response_json_schema":
                        BatchResult.model_json_schema(),

                    "thinking_config": {
                        "thinking_level":
                            THINKING_LEVEL
                    },
                },
            )

            if not response.text:

                raise ValueError(
                    "Empty Gemini response"
                )

            parsed = BatchResult.model_validate_json(
                response.text
            )

            results = parsed.results

            # ------------------------------------------------
            # VALIDATION
            # ------------------------------------------------

            returned_indices = {
                r.index for r in results
            }

            expected_indices = set(
                indices
            )

            if returned_indices != expected_indices:

                missing = (
                    expected_indices -
                    returned_indices
                )

                extra = (
                    returned_indices -
                    expected_indices
                )

                raise ValueError(
                    f"Index mismatch | "
                    f"Missing={sorted(missing)} "
                    f"Extra={sorted(extra)}"
                )

            if len(results) != len(indices):

                raise ValueError(
                    f"Expected {len(indices)} results, "
                    f"received {len(results)}"
                )

            elapsed = (
                time.time() -
                start_time
            )

            speed = (
                len(indices) / elapsed
                if elapsed > 0
                else 0
            )

            log(
                "✓ Batch validated"
            )

            log(
                f"[Worker] Batch {batch_number} "
                f"completed in {elapsed:.2f}s "
                f"| {speed:.2f} reviews/sec"
            )

            return results

        except Exception as e:

            log(
                f"⚠ Batch failed: "
                f"{type(e).__name__}: {e}"
            )

            if attempt < MAX_ATTEMPTS:

                wait_time = min(
                    2 ** attempt +
                    random.random(),
                    10
                )

                log(
                    f"↳ Retrying in "
                    f"{wait_time:.1f}s..."
                )

                time.sleep(
                    wait_time
                )

            else:

                log(
                    f"✗ Batch {batch_number} "
                    f"failed after "
                    f"{MAX_ATTEMPTS} attempts"
                )

                return None


# ============================================================
# PRODUCTION GEMINI PIPELINE
# ============================================================

def predict_gemini(
    df: pd.DataFrame,
    progress_callback=None
):

    total_start = time.time()

    print()
    print(
        "# Gemini 3.1 Flash-Lite "
        "Parallel LLM Pipeline"
    )
    print()

    print(
        f"Model          : {MODEL}"
    )

    print(
        f"Batch Size     : {BATCH_SIZE}"
    )

    print(
        f"Thinking Level : "
        f"{THINKING_LEVEL}"
    )

    print(
        f"Parallel Workers: "
        f"{PARALLEL_WORKERS}"
    )

    # ========================================================
    # INPUT VALIDATION
    # ========================================================

    if not isinstance(
        df,
        pd.DataFrame
    ):

        raise TypeError(
            "predict_gemini() expects "
            "a pandas DataFrame."
        )

    if df.empty:

        raise ValueError(
            "Input CSV contains no records."
        )

    # --------------------------------------------------------
    # Required user columns
    # --------------------------------------------------------

    required_columns = {
        "rating",
        "content"
    }

    missing_columns = (
        required_columns -
        set(df.columns)
    )

    if missing_columns:

        raise ValueError(
            "Missing required column(s): "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    # --------------------------------------------------------
    # Only the two user-provided columns are used.
    # --------------------------------------------------------

    working_df = df[
        ["rating", "content"]
    ].copy()

    # --------------------------------------------------------
    # Validate content
    # --------------------------------------------------------

    working_df["content"] = (
        working_df["content"]
        .fillna("")
        .astype(str)
    )

    if all(
        not text.strip()
        for text in working_df["content"]
    ):

        raise ValueError(
            "Column 'content' contains "
            "no review text."
        )

    # ========================================================
    # INTERNAL INDEX
    # ========================================================

    working_df = working_df.reset_index(
        drop=True
    )

    working_df["__index"] = range(
        len(working_df)
    )

    total_reviews = len(
        working_df
    )

    # ========================================================
    # CREATE BATCHES
    # ========================================================

    batches = []

    for start in range(
        0,
        total_reviews,
        BATCH_SIZE
    ):

        batch_df = working_df.iloc[
            start:start + BATCH_SIZE
        ].copy()

        batches.append(
            batch_df
        )

    total_batches = len(
        batches
    )

    print(
        f"Reviews        : "
        f"{total_reviews}"
    )

    print(
        f"Total Batches  : "
        f"{total_batches}"
    )

    print()

    # ========================================================
    # INITIAL PROGRESS
    # ========================================================

    if progress_callback:

        progress_callback({

            "status":
                "processing",

            "total_reviews":
                total_reviews,

            "total_batches":
                total_batches,

            "completed_batches":
                0,

            "current_batch":
                None,

            "message":
                (
                    "Starting Gemini "
                    "3.1 Flash-Lite analysis"
                )
        })

    # ========================================================
    # PARALLEL PROCESSING
    # ========================================================

    all_results = {}

    completed = 0

    with ThreadPoolExecutor(
        max_workers=PARALLEL_WORKERS
    ) as executor:

        futures = {

            executor.submit(
                process_batch,
                batch_number,
                batch_df
            ): batch_number

            for batch_number, batch_df
            in enumerate(
                batches,
                start=1
            )
        }

        for future in as_completed(
            futures
        ):

            batch_number = futures[
                future
            ]

            try:

                results = future.result()

                if results is None:

                    raise RuntimeError(
                        f"Batch {batch_number} failed."
                    )

                for result in results:

                    all_results[
                        result.index
                    ] = result

                completed += 1

                log(
                    f"✓ Completed "
                    f"{completed}/"
                    f"{total_batches} batches"
                )

                # --------------------------------------------
                # REAL FRONTEND PROGRESS
                # --------------------------------------------

                if progress_callback:

                    progress_callback({

                        "status":
                            "processing",

                        "total_reviews":
                            total_reviews,

                        "total_batches":
                            total_batches,

                        "completed_batches":
                            completed,

                        "current_batch":
                            batch_number,

                        "message":
                            (
                                f"Batch "
                                f"{batch_number}/"
                                f"{total_batches} "
                                f"completed"
                            )
                    })

            except Exception as e:

                log(
                    f"✗ Batch {batch_number} "
                    f"ERROR: {e}"
                )

                if progress_callback:

                    progress_callback({

                        "status":
                            "failed",

                        "total_reviews":
                            total_reviews,

                        "total_batches":
                            total_batches,

                        "completed_batches":
                            completed,

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

    # ========================================================
    # VALIDATE EVERYTHING
    # ========================================================

    expected = set(
        range(total_reviews)
    )

    received = set(
        all_results.keys()
    )

    missing = (
        expected -
        received
    )

    if missing:

        raise RuntimeError(
            f"Pipeline incomplete. "
            f"Missing indices: "
            f"{sorted(missing)}"
        )

    # ========================================================
    # BUILD OUTPUT
    # ========================================================

    output_rows = []

    for index in range(
        total_reviews
    ):

        original_row = (
            working_df.iloc[index]
        )

        result = all_results[
            index
        ]

        output_rows.append({

            "rating":
                original_row["rating"],

            "content":
                original_row["content"],

            "llm_summary":
                result.llm_summary,

            "llm_sentiment":
                result.llm_sentiment,

            "llm_theme":
                result.llm_theme,

            "llm_reason":
                result.llm_reason
        })

    result_df = pd.DataFrame(
        output_rows
    )

    # ========================================================
    # FINAL STATISTICS
    # ========================================================

    total_time = (
        time.time() -
        total_start
    )

    overall_speed = (
        total_reviews / total_time
        if total_time > 0
        else 0
    )

    statistics = {

        "model":
            MODEL,

        "total_reviews":
            total_reviews,

        "batch_size":
            BATCH_SIZE,

        "parallel_workers":
            PARALLEL_WORKERS,

        "thinking_level":
            THINKING_LEVEL,

        "processing_time":
            round(
                total_time,
                2
            ),

        "reviews_per_second":
            round(
                overall_speed,
                2
            )
    }

    print()
    print(
        "=" * 60
    )

    print(
        f"Total Reviews     : "
        f"{total_reviews}"
    )

    print(
        f"Workers           : "
        f"{PARALLEL_WORKERS}"
    )

    print(
        f"Batch Size        : "
        f"{BATCH_SIZE}"
    )

    print(
        f"Processing Time   : "
        f"{total_time:.2f}s"
    )

    print(
        f"Reviews/sec       : "
        f"{overall_speed:.2f}"
    )

    print(
        "=" * 60
    )

    # ========================================================
    # FINAL PROGRESS
    # ========================================================

    if progress_callback:

        progress_callback({

            "status":
                "completed",

            "total_reviews":
                total_reviews,

            "total_batches":
                total_batches,

            "completed_batches":
                total_batches,

            "current_batch":
                total_batches,

            "message":
                "Gemini analysis completed",

            "processing_time":
                round(
                    total_time,
                    2
                ),

            "reviews_per_second":
                round(
                    overall_speed,
                    2
                )
        })

    return result_df, statistics