import { useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import {
    ArrowLeft,
    Download,
    Search,
    Brain,
    Clock3,
    FileText,
    Star
} from "lucide-react";

import {
    downloadResult
} from "../services/api";

import "./QwenResults.css";


function QwenResults() {

    const location = useLocation();
    const navigate = useNavigate();

    const data = location.state;


    const [search, setSearch] = useState("");

    const [sentimentFilter, setSentimentFilter] =
        useState("All");

    const [themeFilter, setThemeFilter] =
        useState("All");

    const [isDownloading, setIsDownloading] =
        useState(false);


    // =========================================================
    // NO DATA
    // =========================================================

    if (!data) {

        return (

            <main className="qwen-results-container">

                <div className="qwen-results-empty">

                    <Brain size={40} />

                    <h2>
                        No analysis results found
                    </h2>

                    <p>
                        Please run a Qwen analysis first.
                    </p>

                    <button
                        onClick={() =>
                            navigate("/qwen")
                        }
                    >
                        Go to Qwen Analysis
                    </button>

                </div>

            </main>

        );

    }


    // =========================================================
    // COMPLETE DATASET
    // =========================================================

    const reviews =
        Array.isArray(data.data)
            ? data.data
            : [];


    const statistics =
        data.statistics || {};


    const totalReviews =
        reviews.length ||
        statistics.total_reviews ||
        data.total_reviews ||
        0;


    // =========================================================
    // AVERAGE RATING
    // =========================================================

    const averageRating = useMemo(() => {

        if (!reviews.length) {
            return 0;
        }

        const total = reviews.reduce(
            (sum, review) =>
                sum + Number(review.rating || 0),
            0
        );

        return total / reviews.length;

    }, [reviews]);


    // =========================================================
    // RATING DISTRIBUTION
    // =========================================================

    const ratingCounts = useMemo(() => {

        const counts = {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0
        };


        reviews.forEach((review) => {

            const rating =
                Number(review.rating);


            if (
                Object.prototype.hasOwnProperty.call(
                    counts,
                    rating
                )
            ) {
                counts[rating]++;
            }

        });


        return counts;

    }, [reviews]);


    // =========================================================
    // SENTIMENT
    // =========================================================

    const sentimentCounts = useMemo(() => {

        const counts = {
            Positive: 0,
            Neutral: 0,
            Negative: 0
        };


        reviews.forEach((review) => {

            const sentiment =
                review.llm_sentiment;


            if (
                sentiment === "Positive" ||
                sentiment === "Neutral" ||
                sentiment === "Negative"
            ) {

                counts[sentiment]++;

            }

        });


        return counts;

    }, [reviews]);


    const sentimentPercentages =
        useMemo(() => {

            if (!totalReviews) {

                return {
                    Positive: 0,
                    Neutral: 0,
                    Negative: 0
                };

            }


            return {

                Positive:
                    (
                        sentimentCounts.Positive /
                        totalReviews
                    ) * 100,

                Neutral:
                    (
                        sentimentCounts.Neutral /
                        totalReviews
                    ) * 100,

                Negative:
                    (
                        sentimentCounts.Negative /
                        totalReviews
                    ) * 100

            };

        }, [
            sentimentCounts,
            totalReviews
        ]);


    // =========================================================
    // THEMES
    // =========================================================

    const themeCounts = useMemo(() => {

        const counts = {};


        reviews.forEach((review) => {

            const theme =
                review.llm_theme ||
                "Other";


            counts[theme] =
                (counts[theme] || 0) + 1;

        });


        return counts;

    }, [reviews]);


    const sortedThemes = useMemo(() => {

        return Object.entries(themeCounts)
            .sort(
                ([, a], [, b]) =>
                    b - a
            );

    }, [themeCounts]);


    // =========================================================
    // PRIORITY ISSUES
    // =========================================================

    const priorityIssues = useMemo(() => {

        return sortedThemes
            .filter(
                ([theme]) =>
                    theme !== "General Praise"
            )
            .slice(0, 5)
            .map(
                ([theme, count]) => ({

                    theme,

                    count,

                    percentage:
                        totalReviews > 0
                            ? (
                                count /
                                totalReviews
                            ) * 100
                            : 0

                })
            );

    }, [
        sortedThemes,
        totalReviews
    ]);


    // =========================================================
    // REPRESENTATIVE FEEDBACK
    // =========================================================

    const representativeFeedback =
        useMemo(() => {

            return priorityIssues
                .map(({ theme }) => {

                    return reviews.find(
                        (review) =>
                            review.llm_theme ===
                            theme
                    );

                })
                .filter(Boolean);

        }, [
            priorityIssues,
            reviews
        ]);


    // =========================================================
    // FILTERED DATA
    //
    // IMPORTANT:
    // Filtering happens against ALL reviews.
    // =========================================================

    const filteredReviews = useMemo(() => {

        return reviews.filter((review) => {

            const searchText =
                search
                    .toLowerCase()
                    .trim();


            const matchesSearch =
                !searchText ||
                String(
                    review.content || ""
                )
                    .toLowerCase()
                    .includes(searchText) ||

                String(
                    review.llm_summary || ""
                )
                    .toLowerCase()
                    .includes(searchText) ||

                String(
                    review.llm_reason || ""
                )
                    .toLowerCase()
                    .includes(searchText);


            const matchesSentiment =
                sentimentFilter === "All" ||
                review.llm_sentiment ===
                    sentimentFilter;


            const matchesTheme =
                themeFilter === "All" ||
                review.llm_theme ===
                    themeFilter;


            return (
                matchesSearch &&
                matchesSentiment &&
                matchesTheme
            );

        });

    }, [
        reviews,
        search,
        sentimentFilter,
        themeFilter
    ]);


    // =========================================================
    // TABLE PREVIEW
    //
    // Only 20 rows are displayed.
    // =========================================================

    const previewReviews =
        filteredReviews.slice(0, 20);


    // =========================================================
    // DOWNLOAD
    // =========================================================

    const handleDownload = async () => {

        if (!data.file_id) {
            return;
        }


        try {

            setIsDownloading(true);

            await downloadResult(
                data.file_id
            );

        }
        catch (error) {

            console.error(
                "Download failed:",
                error
            );

        }
        finally {

            setIsDownloading(false);

        }

    };


    // =========================================================
    // PERFORMANCE
    // =========================================================

    const processingTime =
        statistics.processing_time ??
        data.processing_time;


    const formattedTime =
        processingTime !== undefined
            ? `${Number(
                processingTime
            ).toFixed(2)}s`
            : "—";


    // =========================================================
    // RENDER
    // =========================================================

    return (

        <main className="qwen-results-container">


            {/* =================================================
                TOP BAR
            ================================================= */}

            <div className="qwen-results-top">

                <button
                    className="qwen-results-back"
                    onClick={() =>
                        navigate("/qwen")
                    }
                >

                    <ArrowLeft size={17} />

                    New Analysis

                </button>


                <button
                    className="qwen-download-button"
                    onClick={handleDownload}
                    disabled={
                        !data.file_id ||
                        isDownloading
                    }
                >

                    <Download size={18} />

                    {isDownloading
                        ? "Preparing..."
                        : "Download CSV"}

                </button>

            </div>


            {/* =================================================
                HERO
            ================================================= */}

            <section className="qwen-results-hero">

                <span className="qwen-results-badge">

                    <Brain size={15} />

                    Qwen3 8B Analysis Complete

                </span>


                <h1>
                    Review Intelligence Results
                </h1>


                <p>
                    A complete analysis of{" "}
                    <strong>
                        {totalReviews}
                    </strong>{" "}
                    reviews using Qwen3 8B.
                </p>

            </section>


            {/* =================================================
                OVERVIEW
            ================================================= */}

            <section className="qwen-results-stats">


                <div className="qwen-stat-card">

                    <div className="qwen-stat-icon">
                        <FileText size={24} />
                    </div>

                    <span>
                        Reviews Analyzed
                    </span>

                    <strong>
                        {totalReviews}
                    </strong>

                </div>


                <div className="qwen-stat-card">

                    <div className="qwen-stat-icon">
                        <Star size={24} />
                    </div>

                    <span>
                        Average Rating
                    </span>

                    <strong>
                        {averageRating.toFixed(2)}
                        <small> / 5</small>
                    </strong>

                </div>


                <div className="qwen-stat-card">

                    <div className="qwen-stat-icon">
                        <Clock3 size={24} />
                    </div>

                    <span>
                        Processing Time
                    </span>

                    <strong>
                        {formattedTime}
                    </strong>

                </div>


                <div className="qwen-stat-card">

                    <div className="qwen-stat-icon">
                        <Brain size={24} />
                    </div>

                    <span>
                        Model
                    </span>

                    <strong>
                        {statistics.model ||
                            data.model ||
                            "qwen3:8b"}
                    </strong>

                </div>


            </section>


            {/* =================================================
                RATING DISTRIBUTION
            ================================================= */}

            <section className="qwen-result-section">

                <div className="qwen-section-heading">

                    <span>
                        DATASET OVERVIEW
                    </span>

                    <h2>
                        Rating Distribution
                    </h2>

                </div>


                <div className="qwen-rating-distribution">

                    {[5, 4, 3, 2, 1].map(
                        (rating) => {

                            const count =
                                ratingCounts[rating];


                            const percentage =
                                totalReviews > 0
                                    ? (
                                        count /
                                        totalReviews
                                    ) * 100
                                    : 0;


                            return (

                                <div
                                    className="qwen-rating-row"
                                    key={rating}
                                >

                                    <span className="qwen-rating-label">

                                        {rating}

                                        <Star
                                            size={14}
                                            fill="currentColor"
                                        />

                                    </span>


                                    <div className="qwen-rating-track">

                                        <div
                                            className="qwen-rating-bar"
                                            style={{
                                                width:
                                                    `${percentage}%`
                                            }}
                                        />

                                    </div>


                                    <span className="qwen-rating-count">
                                        {count}
                                    </span>


                                    <span className="qwen-rating-percent">
                                        {percentage.toFixed(1)}%
                                    </span>

                                </div>

                            );

                        }
                    )}

                </div>

            </section>


            {/* =================================================
                SENTIMENT
            ================================================= */}

            <section className="qwen-result-section">

                <div className="qwen-section-heading">

                    <span>
                        AI SENTIMENT
                    </span>

                    <h2>
                        Review Sentiment
                    </h2>

                </div>


                <div className="qwen-sentiment-grid">

                    {[
                        "Positive",
                        "Neutral",
                        "Negative"
                    ].map((sentiment) => (

                        <div
                            key={sentiment}
                            className={
                                `qwen-sentiment-card ${
                                    sentiment.toLowerCase()
                                }`
                            }
                            onClick={() =>
                                setSentimentFilter(
                                    sentimentFilter ===
                                        sentiment
                                        ? "All"
                                        : sentiment
                                )
                            }
                        >

                            <span>
                                {sentiment}
                            </span>


                            <strong>
                                {
                                    sentimentCounts[
                                        sentiment
                                    ]
                                }
                            </strong>


                            <small>

                                {
                                    sentimentPercentages[
                                        sentiment
                                    ].toFixed(1)
                                }%

                            </small>

                        </div>

                    ))}

                </div>

            </section>


            {/* =================================================
                THEMES
            ================================================= */}

            <section className="qwen-result-section">

                <div className="qwen-section-heading">

                    <span>
                        AI THEME DETECTION
                    </span>

                    <h2>
                        Review Themes
                    </h2>

                    <p>
                        Themes are generated from the
                        complete analyzed dataset.
                    </p>

                </div>


                <div className="qwen-theme-list">

                    {sortedThemes.map(
                        ([theme, count]) => {

                            const percentage =
                                totalReviews > 0
                                    ? (
                                        count /
                                        totalReviews
                                    ) * 100
                                    : 0;


                            return (

                                <button
                                    key={theme}
                                    className={
                                        themeFilter === theme
                                            ? "qwen-theme active"
                                            : "qwen-theme"
                                    }
                                    onClick={() =>
                                        setThemeFilter(
                                            themeFilter === theme
                                                ? "All"
                                                : theme
                                        )
                                    }
                                >

                                    <span>
                                        {theme}
                                    </span>

                                    <strong>
                                        {count}
                                    </strong>

                                    <small>
                                        {percentage.toFixed(1)}%
                                    </small>

                                </button>

                            );

                        }
                    )}

                </div>

            </section>


            {/* =================================================
                PRIORITY ISSUES
            ================================================= */}

            {priorityIssues.length > 0 && (

                <section className="qwen-result-section">

                    <div className="qwen-section-heading">

                        <span>
                            KEY ISSUES
                        </span>

                        <h2>
                            Priority Review Themes
                        </h2>

                        <p>
                            Most frequent non-praise themes
                            identified across the complete dataset.
                        </p>

                    </div>


                    <div className="qwen-priority-grid">

                        {priorityIssues.map(
                            (issue, index) => (

                                <button
                                    className="qwen-priority-card"
                                    key={issue.theme}
                                    onClick={() =>
                                        setThemeFilter(
                                            issue.theme
                                        )
                                    }
                                >

                                    <span className="qwen-priority-number">
                                        #{index + 1}
                                    </span>


                                    <div className="qwen-priority-content">

                                        <h3>
                                            {issue.theme}
                                        </h3>

                                        <p>
                                            {issue.count} reviews
                                        </p>

                                    </div>


                                    <strong>
                                        {issue.percentage.toFixed(1)}%
                                    </strong>

                                </button>

                            )
                        )}

                    </div>

                </section>

            )}


            {/* =================================================
                REPRESENTATIVE FEEDBACK
            ================================================= */}

            {representativeFeedback.length > 0 && (

                <section className="qwen-result-section">

                    <div className="qwen-section-heading">

                        <span>
                            REPRESENTATIVE FEEDBACK
                        </span>

                        <h2>
                            What Users Are Saying
                        </h2>

                        <p>
                            Representative examples selected
                            from the most frequent issue themes.
                        </p>

                    </div>


                    <div className="qwen-feedback-grid">

                        {representativeFeedback.map(
                            (review, index) => (

                                <article
                                    className="qwen-feedback-card"
                                    key={`${review.llm_theme}-${index}`}
                                >

                                    <div className="qwen-feedback-header">

                                        <span className="qwen-theme-pill">
                                            {review.llm_theme}
                                        </span>


                                        <span
                                            className={
                                                `qwen-sentiment-pill ${
                                                    String(
                                                        review.llm_sentiment
                                                    ).toLowerCase()
                                                }`
                                            }
                                        >
                                            {review.llm_sentiment}
                                        </span>

                                    </div>


                                    <p className="qwen-feedback-review">

                                        “{review.content}”

                                    </p>


                                    <div className="qwen-feedback-summary">

                                        <strong>
                                            Qwen Summary
                                        </strong>

                                        <p>
                                            {review.llm_summary}
                                        </p>

                                    </div>


                                    <div className="qwen-feedback-reason">

                                        <strong>
                                            Reason
                                        </strong>

                                        <p>
                                            {review.llm_reason}
                                        </p>

                                    </div>

                                </article>

                            )
                        )}

                    </div>

                </section>

            )}


            {/* =================================================
                REVIEW PREVIEW
            ================================================= */}

            <section className="qwen-result-section">

                <div className="qwen-table-heading">

                    <div>

                        <span>
                            REVIEW PREVIEW
                        </span>

                        <h2>
                            Review Details
                        </h2>

                    </div>


                    <span className="qwen-result-count">

                        Showing{" "}
                        {Math.min(
                            20,
                            filteredReviews.length
                        )}
                        {" "}of{" "}
                        {totalReviews}

                    </span>

                </div>


                <div className="qwen-filters">

                    <div className="qwen-search">

                        <Search size={18} />

                        <input
                            type="text"
                            placeholder="Search reviews, summaries or reasons..."
                            value={search}
                            onChange={(event) =>
                                setSearch(
                                    event.target.value
                                )
                            }
                        />

                    </div>


                    <select
                        value={sentimentFilter}
                        onChange={(event) =>
                            setSentimentFilter(
                                event.target.value
                            )
                        }
                    >

                        <option value="All">
                            All Sentiments
                        </option>

                        <option value="Positive">
                            Positive
                        </option>

                        <option value="Neutral">
                            Neutral
                        </option>

                        <option value="Negative">
                            Negative
                        </option>

                    </select>


                    <select
                        value={themeFilter}
                        onChange={(event) =>
                            setThemeFilter(
                                event.target.value
                            )
                        }
                    >

                        <option value="All">
                            All Themes
                        </option>

                        {sortedThemes.map(
                            ([theme]) => (

                                <option
                                    key={theme}
                                    value={theme}
                                >
                                    {theme}
                                </option>

                            )
                        )}

                    </select>

                </div>


                <div className="qwen-table-wrapper">

                    <table className="qwen-results-table">

                        <thead>

                            <tr>

                                <th>#</th>

                                <th>
                                    Rating
                                </th>

                                <th>
                                    Review
                                </th>

                                <th>
                                    Summary
                                </th>

                                <th>
                                    Sentiment
                                </th>

                                <th>
                                    Theme
                                </th>

                                <th>
                                    Reason
                                </th>

                            </tr>

                        </thead>


                        <tbody>

                            {previewReviews.length === 0 ? (

                                <tr>

                                    <td
                                        colSpan="7"
                                        className="qwen-no-results"
                                    >
                                        No reviews match
                                        the selected filters.
                                    </td>

                                </tr>

                            ) : (

                                previewReviews.map(
                                    (review, index) => (

                                        <tr
                                            key={`${review.content}-${index}`}
                                        >

                                            <td>
                                                {index + 1}
                                            </td>


                                            <td>

                                                <span className="qwen-rating">

                                                    {review.rating}

                                                </span>

                                            </td>


                                            <td className="qwen-review-content">

                                                {review.content}

                                            </td>


                                            <td>

                                                {review.llm_summary}

                                            </td>


                                            <td>

                                                <span
                                                    className={
                                                        `qwen-sentiment-pill ${
                                                            String(
                                                                review.llm_sentiment
                                                            ).toLowerCase()
                                                        }`
                                                    }
                                                >
                                                    {
                                                        review.llm_sentiment
                                                    }
                                                </span>

                                            </td>


                                            <td>

                                                <span className="qwen-theme-pill">

                                                    {
                                                        review.llm_theme
                                                    }

                                                </span>

                                            </td>


                                            <td className="qwen-reason">

                                                {
                                                    review.llm_reason
                                                }

                                            </td>

                                        </tr>

                                    )
                                )

                            )}

                        </tbody>

                    </table>

                </div>

            </section>


            {/* =================================================
                DOWNLOAD
            ================================================= */}

            <section className="qwen-download-section">

                <div>

                    <span className="qwen-download-label">
                        COMPLETE ANALYSIS
                    </span>

                    <h2>
                        Your Qwen report is ready
                    </h2>

                    <p>
                        Download the complete dataset with
                        every review, Qwen summary, sentiment,
                        theme, and reasoning result.
                    </p>

                </div>


                <button
                    className="qwen-download-button large"
                    onClick={handleDownload}
                    disabled={
                        !data.file_id ||
                        isDownloading
                    }
                >

                    <Download size={19} />

                    {isDownloading
                        ? "Preparing..."
                        : "Download Complete CSV"}

                </button>

            </section>


        </main>

    );

}


export default QwenResults;