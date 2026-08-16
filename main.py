from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

import pandas as pd
import os
import math
import numpy as np

import uuid
import threading
from concurrent.futures import ThreadPoolExecutor

from utils import generate_file_id, get_output_path
from predict import predict_dataframe

from llm_pipeline import predict_llm
from gemini_pipeline import predict_gemini


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="AI App Review Analyzer",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# BACKGROUND JOB SYSTEM
# ============================================================

jobs = {}

job_executor = ThreadPoolExecutor(
    max_workers=4
)


# ============================================================
# JSON CLEANING
# ============================================================

def clean_for_json(obj):

    if isinstance(obj, dict):

        return {
            key: clean_for_json(value)
            for key, value in obj.items()
        }

    if isinstance(obj, list):

        return [
            clean_for_json(value)
            for value in obj
        ]

    if isinstance(obj, tuple):

        return [
            clean_for_json(value)
            for value in obj
        ]

    if isinstance(obj, (float, np.floating)):

        if not math.isfinite(float(obj)):
            return None

        return float(obj)

    if isinstance(obj, (int, np.integer)):

        return int(obj)

    return obj


# ============================================================
# COMMON CSV VALIDATION
# ============================================================

def load_and_validate_csv(file):

    # --------------------------------------------------------
    # Validate extension
    # --------------------------------------------------------

    if (
        not file.filename
        or not file.filename.lower().endswith(".csv")
    ):

        raise ValueError(
            "Please upload a CSV file."
        )

    # --------------------------------------------------------
    # Read CSV
    # --------------------------------------------------------

    df = pd.read_csv(file.file)

    # --------------------------------------------------------
    # Normalize column names
    # --------------------------------------------------------

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    # --------------------------------------------------------
    # Empty CSV
    # --------------------------------------------------------

    if df.empty:

        raise ValueError(
            "Uploaded CSV is empty."
        )

    # --------------------------------------------------------
    # Required columns
    # --------------------------------------------------------

    required_columns = {
        "rating",
        "content"
    }

    missing = (
        required_columns -
        set(df.columns)
    )

    if missing:

        raise ValueError(
            "Missing required column(s): "
            + ", ".join(sorted(missing))
        )

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    if (
        df["rating"].isnull().any()
        or df["content"].isnull().any()
    ):

        raise ValueError(
            "Columns 'rating' and 'content' "
            "must not contain empty values."
        )

    # --------------------------------------------------------
    # Only accepted input columns
    # --------------------------------------------------------

    return df[
        ["rating", "content"]
    ].copy()


# ============================================================
# CREATE JOB
# ============================================================

def create_job(model, total_reviews):

    job_id = str(uuid.uuid4())

    total_batches = (
        (total_reviews + 31) // 32
    )

    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "model": model,
        "total_reviews": total_reviews,
        "total_batches": total_batches,
        "completed_batches": 0,
        "current_batch": None,
        "message": "Waiting to start...",
        "file_id": None,
        "statistics": None,
        "preview": None,
        "data": None,
        "error": None
    }

    return job_id


# ============================================================
# UPDATE JOB
# ============================================================

def update_job(job_id, **updates):

    if job_id not in jobs:
        return

    jobs[job_id].update(updates)


# ============================================================
# PROGRESS CALLBACK
# ============================================================

def make_progress_callback(job_id):

    def progress_callback(progress):

        update_job(
            job_id,
            **progress
        )

    return progress_callback


# ============================================================
# QWEN BACKGROUND JOB
# ============================================================

def run_qwen_job(job_id, df):

    try:

        update_job(
            job_id,
            status="processing",
            message="Starting Qwen3 8B..."
        )

        progress_callback = (
            make_progress_callback(job_id)
        )

        result_df, statistics = predict_llm(
            df,
            progress_callback=progress_callback
        )

        # ----------------------------------------------------
        # Save result
        # ----------------------------------------------------

        file_id = generate_file_id()

        output_path = get_output_path(
            file_id
        )

        result_df.to_csv(
            output_path,
            index=False,
            encoding="utf-8-sig"
        )

        # ----------------------------------------------------
        # Complete
        # ----------------------------------------------------

        update_job(
            job_id,

            status="completed",

            completed_batches=
                jobs[job_id]["total_batches"],

            current_batch=
                jobs[job_id]["total_batches"],

            message="Analysis completed",

            file_id=file_id,

            statistics=statistics,

            preview=
                result_df
                .head(20)
                .to_dict(
                    orient="records"
                ),

            data=
                result_df
                .to_dict(
                    orient="records"
                )
        )

    except Exception as e:

        update_job(
            job_id,
            status="failed",
            message="Qwen analysis failed",
            error=str(e)
        )


# ============================================================
# GEMINI BACKGROUND JOB
# ============================================================

def run_gemini_job(job_id, df):

    try:

        update_job(
            job_id,
            status="processing",
            message="Starting Gemini..."
        )

        progress_callback = (
            make_progress_callback(job_id)
        )

        result_df, statistics = predict_gemini(
            df,
            progress_callback=progress_callback
        )

        # ----------------------------------------------------
        # Save result
        # ----------------------------------------------------

        file_id = generate_file_id()

        output_path = get_output_path(
            file_id
        )

        result_df.to_csv(
            output_path,
            index=False,
            encoding="utf-8-sig"
        )

        # ----------------------------------------------------
        # Complete
        # ----------------------------------------------------

        update_job(
            job_id,

            status="completed",

            completed_batches=
                jobs[job_id]["total_batches"],

            current_batch=
                jobs[job_id]["total_batches"],

            message="Analysis completed",

            file_id=file_id,

            statistics=statistics,

            preview=
                result_df
                .head(20)
                .to_dict(
                    orient="records"
                ),
            data=
                result_df
                .to_dict(
                    orient="records"
                )
        )

    except Exception as e:

        update_job(
            job_id,
            status="failed",
            message="Gemini analysis failed",
            error=str(e)
        )


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Backend Running Successfully"
    }


# ============================================================
# DOWNLOAD RESULTS
# ============================================================

@app.get("/download/{file_id}")
def download(file_id: str):

    output_path = get_output_path(
        file_id
    )

    if not os.path.exists(output_path):

        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": "Result file not found."
            }
        )

    return FileResponse(
        path=output_path,
        filename="analysis_results.csv",
        media_type="text/csv"
    )


# ============================================================
# TRADITIONAL ML ANALYSIS
# ============================================================

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...)
):

    try:

        df = load_and_validate_csv(file)

        result_df, statistics = (
            predict_dataframe(df)
        )

        file_id = generate_file_id()

        output_path = get_output_path(
            file_id
        )

        result_df.to_csv(
            output_path,
            index=False
        )

        response_data = {
            "success": True,
            "model": "traditional_ml",
            "file_id": file_id,
            "statistics": statistics,
            "preview":
                result_df
                .head(20)
                .to_dict(
                    orient="records"
                )
        }

        return JSONResponse(
            content=clean_for_json(
                response_data
            )
        )

    except ValueError as e:

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": str(e)
            }
        )

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


# ============================================================
# START QWEN JOB
# ============================================================

@app.post("/analyze/qwen")
async def analyze_qwen(
    file: UploadFile = File(...)
):

    try:

        df = load_and_validate_csv(file)

        job_id = create_job(
            model="qwen3:8b",
            total_reviews=len(df)
        )

        job_executor.submit(
            run_qwen_job,
            job_id,
            df
        )

        return {
            "success": True,
            "job_id": job_id,
            "model": "qwen3:8b",
            "status": "queued"
        }

    except ValueError as e:

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": str(e)
            }
        )

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


# ============================================================
# START GEMINI JOB
# ============================================================

@app.post("/analyze/gemini")
async def analyze_gemini(
    file: UploadFile = File(...)
):

    try:

        df = load_and_validate_csv(file)

        job_id = create_job(
            model="gemini-3.1-flash-lite",
            total_reviews=len(df)
        )

        job_executor.submit(
            run_gemini_job,
            job_id,
            df
        )

        return {
            "success": True,
            "job_id": job_id,
            "model": "gemini-3.1-flash-lite",
            "status": "queued"
        }

    except ValueError as e:

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": str(e)
            }
        )

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


# ============================================================
# GET JOB PROGRESS
# ============================================================

@app.get("/progress/{job_id}")
def get_progress(job_id: str):

    if job_id not in jobs:

        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": "Job not found."
            }
        )

    job = jobs[job_id].copy()

    return JSONResponse(
        content=clean_for_json(job)
    )