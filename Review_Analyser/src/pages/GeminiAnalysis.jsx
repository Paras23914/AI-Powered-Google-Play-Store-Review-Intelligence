import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
    Brain,
    BarChart3,
    Zap,
    FileSpreadsheet,
    Upload,
    Loader2,
    CheckCircle2,
    AlertCircle,
    ArrowLeft
} from "lucide-react";

import {
    uploadGeminiCSV,
    getAnalysisProgress
} from "../services/api";

import "./GeminiAnalysis.css";


function GeminiAnalysis() {

    const navigate = useNavigate();

    const fileInputRef = useRef(null);
    const pollingRef = useRef(null);

    const [selectedFile, setSelectedFile] =
        useState(null);

    const [jobId, setJobId] =
        useState(null);

    const [progress, setProgress] =
        useState(null);

    const [isStarting, setIsStarting] =
        useState(false);

    const [error, setError] =
        useState("");


    // =========================================================
    // CLEANUP
    // =========================================================

    useEffect(() => {

        return () => {

            if (pollingRef.current) {

                clearInterval(
                    pollingRef.current
                );

            }

        };

    }, []);


    // =========================================================
    // FILE SELECTION
    // =========================================================

    const handleChooseFile = () => {

        fileInputRef.current?.click();

    };


    const handleFileChange = (event) => {

        const file =
            event.target.files?.[0];

        if (!file) return;


        if (
            !file.name
                .toLowerCase()
                .endsWith(".csv")
        ) {

            setError(
                "Please select a CSV file."
            );

            setSelectedFile(null);

            return;

        }


        setSelectedFile(file);

        setError("");

        setJobId(null);

        setProgress(null);

    };


    // =========================================================
    // START GEMINI ANALYSIS
    // =========================================================

    const handleAnalyze = async () => {

        if (!selectedFile) return;


        try {

            setError("");

            setIsStarting(true);

            setProgress(null);


            const response =
                await uploadGeminiCSV(
                    selectedFile
                );


            if (!response?.job_id) {

                throw new Error(
                    "The backend did not return a job ID."
                );

            }


            setJobId(
                response.job_id
            );

            setProgress(
                response
            );

            setIsStarting(false);

        }
        catch (err) {

            console.error(
                "Gemini start error:",
                err
            );


            const message =
                err?.response?.data?.error ||
                err?.message ||
                "Unable to start Gemini analysis.";


            setError(message);

            setIsStarting(false);

        }

    };


    // =========================================================
    // PROGRESS POLLING
    // =========================================================

    useEffect(() => {

        if (!jobId) return;


        let cancelled = false;


        const checkProgress = async () => {

            try {

                const data =
                    await getAnalysisProgress(
                        jobId
                    );


                if (cancelled) return;


                setProgress(data);


                // =============================================
                // COMPLETED
                // =============================================

                if (
                    data.status ===
                    "completed"
                ) {

                    if (
                        pollingRef.current
                    ) {

                        clearInterval(
                            pollingRef.current
                        );

                        pollingRef.current =
                            null;

                    }


                    navigate(
                        "/gemini-results",
                        {
                            state: data
                        }
                    );


                    return;

                }


                // =============================================
                // FAILED
                // =============================================

                if (
                    data.status === "failed" ||
                    data.status === "error"
                ) {

                    if (
                        pollingRef.current
                    ) {

                        clearInterval(
                            pollingRef.current
                        );

                        pollingRef.current =
                            null;

                    }


                    setError(
                        data.error ||
                        data.message ||
                        "Gemini analysis failed."
                    );

                }

            }
            catch (err) {

                console.error(
                    "Gemini progress error:",
                    err
                );

                /*
                 * Do not immediately stop the analysis.
                 *
                 * A temporary request failure should not
                 * terminate a running Gemini job.
                 */

            }

        };


        // Check immediately

        checkProgress();


        // Continue checking every second

        pollingRef.current =
            setInterval(
                checkProgress,
                1000
            );


        return () => {

            cancelled = true;


            if (
                pollingRef.current
            ) {

                clearInterval(
                    pollingRef.current
                );

                pollingRef.current =
                    null;

            }

        };

    }, [
        jobId,
        navigate
    ]);


    // =========================================================
    // PROGRESS VALUES
    // =========================================================

    const totalBatches =
        progress?.total_batches || 0;


    const completedBatches =
        progress?.completed_batches || 0;


    const percentage =
        totalBatches > 0
            ? Math.round(
                (
                    completedBatches /
                    totalBatches
                ) * 100
            )
            : 0;


    const isProcessing =
        Boolean(jobId) &&
        progress?.status !==
            "completed" &&
        !error;


    // =========================================================
    // BACK
    // =========================================================

    const handleBack = () => {

        if (
            pollingRef.current
        ) {

            clearInterval(
                pollingRef.current
            );

            pollingRef.current =
                null;

        }


        navigate("/");

    };


    // =========================================================
    // UI
    // =========================================================

    return (

        <main className="gemini-container">


            {/* =================================================
                BACK BUTTON
            ================================================= */}

            <button
                className="gemini-back"
                onClick={handleBack}
            >

                <ArrowLeft size={17} />

                Back to Analysis Selection

            </button>


            {/* =================================================
                HERO
            ================================================= */}

            <section className="gemini-hero">

                <span className="gemini-hero-badge">

                    <Brain size={15} />

                    Advanced LLM Intelligence

                </span>


                <h1 className="gemini-title">

                    Gemini Review Intelligence

                </h1>


                <p className="gemini-subtitle">

                    Analyze Google Play Store reviews
                    using Google's online Gemini model
                    to generate summaries, sentiment,
                    themes, and reasoning.

                </p>

            </section>


            {/* =================================================
                MAIN ANALYSIS CARD
            ================================================= */}

            <section className="gemini-analysis-card">


                {/* =================================================
                    UPLOAD
                ================================================= */}

                {!jobId && !error && (

                    <>

                        <div className="gemini-upload-icon">

                            <FileSpreadsheet
                                size={34}
                            />

                        </div>


                        <h2>

                            Upload Review Dataset

                        </h2>


                        <p className="gemini-card-description">

                            Provide a CSV containing
                            the required
                            <strong> rating </strong>
                            and
                            <strong> content </strong>
                            columns.

                        </p>


                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".csv"
                            onChange={
                                handleFileChange
                            }
                            hidden
                        />


                        <button
                            className="gemini-choose-button"
                            onClick={
                                handleChooseFile
                            }
                        >

                            <Upload size={18} />

                            Choose CSV

                        </button>


                        {selectedFile && (

                            <div className="gemini-file">

                                <FileSpreadsheet
                                    size={18}
                                />

                                <span>

                                    {selectedFile.name}

                                </span>

                            </div>

                        )}


                        <button
                            className="gemini-analyze-button"
                            disabled={
                                !selectedFile ||
                                isStarting
                            }
                            onClick={
                                handleAnalyze
                            }
                        >

                            {isStarting ? (

                                <>

                                    <Loader2
                                        size={18}
                                        className="gemini-spin"
                                    />

                                    Starting Analysis...

                                </>

                            ) : (

                                <>

                                    <Brain
                                        size={18}
                                    />

                                    Analyze with Gemini

                                </>

                            )}

                        </button>


                        <div className="gemini-requirements">

                            <strong>
                                CSV Requirements
                            </strong>


                            <ul>

                                <li>
                                    File must be in CSV format
                                </li>

                                <li>
                                    Required column:
                                    <strong> rating</strong>
                                </li>

                                <li>
                                    Required column:
                                    <strong> content</strong>
                                </li>

                                <li>
                                    Required columns must not
                                    contain empty values
                                </li>

                            </ul>

                        </div>

                    </>

                )}


                {/* =================================================
                    PROCESSING
                ================================================= */}

                {isProcessing && (

                    <div className="gemini-processing">


                        <div className="gemini-processing-icon">

                            <Loader2
                                size={40}
                                className="gemini-spin"
                            />

                        </div>


                        <span className="gemini-processing-label">

                            GEMINI

                        </span>


                        <h2>

                            Analyzing Reviews

                        </h2>


                        <p>

                            Gemini is processing your
                            review dataset using the
                            online Gemini API. This may
                            take some time depending
                            on the number of reviews.

                        </p>


                        {/* =========================================
                            PROGRESS
                        ========================================= */}

                        <div className="gemini-progress-section">

                            <div className="gemini-progress-header">

                                <span>
                                    Batch Progress
                                </span>

                                <strong>

                                    {completedBatches}
                                    /
                                    {totalBatches}

                                </strong>

                            </div>


                            <div className="gemini-progress-track">

                                <div
                                    className="gemini-progress-bar"
                                    style={{
                                        width:
                                            `${percentage}%`
                                    }}
                                />

                            </div>


                            <div className="gemini-progress-percent">

                                {percentage}%

                            </div>

                        </div>


                        {/* =========================================
                            STATUS
                        ========================================= */}

                        <div className="gemini-live-status">

                            <Loader2
                                size={16}
                                className="gemini-spin"
                            />

                            <span>

                                {progress?.message ||
                                    "Processing reviews..."}

                            </span>

                        </div>


                        {/* =========================================
                            INFORMATION
                        ========================================= */}

                        <div className="gemini-processing-info">


                            <div>

                                <span>
                                    Reviews
                                </span>

                                <strong>
                                    {
                                        progress?.total_reviews ||
                                        "—"
                                    }
                                </strong>

                            </div>


                            <div>

                                <span>
                                    Model
                                </span>

                                <strong>
                                    {
                                        progress?.model ||
                                        "Gemini"
                                    }
                                </strong>

                            </div>


                            <div>

                                <span>
                                    Workers
                                </span>

                                <strong>
                                    {
                                        progress?.statistics
                                            ?.parallel_workers ||
                                        3
                                    }
                                </strong>

                            </div>

                        </div>


                        {/* =========================================
                            BATCH CHECKLIST
                        ========================================= */}

                        <div className="gemini-batch-list">

                            {Array.from(
                                {
                                    length:
                                        totalBatches
                                },
                                (_, index) => {

                                    const batchNumber =
                                        index + 1;


                                    const completed =
                                        batchNumber <=
                                        completedBatches;


                                    return (

                                        <div
                                            key={
                                                batchNumber
                                            }
                                            className={
                                                completed
                                                    ? "gemini-batch completed"
                                                    : "gemini-batch"
                                            }
                                        >

                                            {completed ? (

                                                <CheckCircle2
                                                    size={16}
                                                />

                                            ) : (

                                                <span>
                                                    {
                                                        batchNumber
                                                    }
                                                </span>

                                            )}


                                            <span>

                                                Batch{" "}
                                                {
                                                    batchNumber
                                                }

                                            </span>


                                            {completed && (

                                                <small>
                                                    Completed
                                                </small>

                                            )}

                                        </div>

                                    );

                                }
                            )}

                        </div>

                    </div>

                )}


                {/* =================================================
                    ERROR
                ================================================= */}

                {error && (

                    <div className="gemini-error">

                        <AlertCircle
                            size={24}
                        />


                        <div>

                            <strong>
                                Unable to analyze dataset
                            </strong>


                            <p>
                                {error}
                            </p>


                            <button
                                onClick={() => {

                                    setError("");

                                    setJobId(null);

                                    setProgress(null);

                                }}
                            >
                                Try Again
                            </button>

                        </div>

                    </div>

                )}

            </section>


            {/* =================================================
                FEATURES
            ================================================= */}

            {!jobId && (

                <section className="features gemini-features">


                    <div className="feature-card">

                        <Brain size={34} />

                        <h3>
                            Natural Language
                        </h3>

                        <p>
                            Generate concise summaries
                            that explain what users are
                            saying.
                        </p>

                    </div>


                    <div className="feature-card">

                        <BarChart3 size={34} />

                        <h3>
                            Sentiment & Themes
                        </h3>

                        <p>
                            Identify sentiment and the
                            most relevant review themes.
                        </p>

                    </div>


                    <div className="feature-card">

                        <Zap size={34} />

                        <h3>
                            Online Gemini AI
                        </h3>

                        <p>
                            Analyze reviews using Google's
                            online Gemini API.
                        </p>

                    </div>


                    <div className="feature-card">

                        <FileSpreadsheet size={34} />

                        <h3>
                            CSV Export
                        </h3>

                        <p>
                            Download the complete
                            Gemini-generated analysis.
                        </p>

                    </div>


                </section>

            )}

        </main>

    );

}


export default GeminiAnalysis;