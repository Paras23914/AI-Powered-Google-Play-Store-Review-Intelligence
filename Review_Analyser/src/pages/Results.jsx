import { useLocation, Navigate } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import {
    ArrowLeft,
    CheckCircle2,
    Download,
    BarChart3,
    Brain,
    Sparkles
} from "lucide-react";

import SectionCard from "../components/Common/SectionCard";
import RatingDistribution from "../components/Charts/RatingDistribution";
import StatsCards from "../components/Cards/StatsCards";
import ModelSection from "../components/Dashboard/ModelSection";
import ComparisonSection from "../components/Dashboard/ComparisonSection";
import PredictionTable from "../components/Table/PredictionTable";
import DownloadButton from "../components/Download/DownloadButton";

import "./Results.css";


function Results() {

    const location = useLocation();
    const navigate = useNavigate();
    if (!location.state) {

        return <Navigate to="/" replace />;

    }

    const response = location.state;

    const statistics = response.statistics;


    return (

        <main className="results-page">
            <button
                className="page-back-button"
                onClick={() => navigate("/")}
            >
                <ArrowLeft size={17} />
                Back to Home
            </button>

            {/* =========================================
                HEADER
            ========================================= */}

            <header className="results-header">

                <div className="results-heading">

                    <div className="results-status">

                        <CheckCircle2 size={17} />

                        Analysis completed

                    </div>

                    <h1>
                        Review Intelligence
                    </h1>

                    <p>

                        Insights generated from{" "}

                        <strong>
                            {statistics.dataset.total_reviews}
                        </strong>{" "}

                        Google Play Store reviews.

                    </p>

                </div>


                <DownloadButton
                    fileId={response.file_id}
                />

            </header>


            {/* =========================================
                OVERVIEW
            ========================================= */}

            <section className="results-overview">

                <StatsCards
                    dataset={statistics.dataset}
                    performance={statistics.performance}
                />

            </section>


            {/* =========================================
                RATING DISTRIBUTION
            ========================================= */}

            <SectionCard title="Rating Distribution">

                <div className="section-intro">

                    <div>

                        <span className="section-kicker">
                            DATASET OVERVIEW
                        </span>

                        <p>
                            Distribution of ratings across
                            the analyzed reviews.
                        </p>

                    </div>

                    <BarChart3 size={22} />

                </div>

                <RatingDistribution
                    ratingData={
                        statistics.dataset.rating_distribution
                    }
                />

            </SectionCard>


            {/* =========================================
                MODEL ANALYSIS
            ========================================= */}

            <div className="model-heading">

                <div>

                    <span className="section-kicker">
                        MODEL ANALYSIS
                    </span>

                    <h2>
                        Compare Analysis Results
                    </h2>

                    <p>
                        Explore how Traditional ML and DeBERTa
                        interpret your reviews.
                    </p>

                </div>

            </div>


            <div className="model-grid">


                {/* Traditional ML */}

                <section className="model-card traditional-model">

                    <div className="model-card-header">

                        <div className="model-icon">

                            <BarChart3 size={22} />

                        </div>

                        <div>

                            <span>
                                CLASSICAL APPROACH
                            </span>

                            <h2>
                                Traditional ML
                            </h2>

                        </div>

                    </div>

                    <ModelSection
                        data={statistics.traditional}
                    />

                </section>


                {/* DeBERTa */}

                <section className="model-card deberta-model">

                    <div className="model-card-header">

                        <div className="model-icon">

                            <Brain size={22} />

                        </div>

                        <div>

                            <span>
                                TRANSFORMER APPROACH
                            </span>

                            <h2>
                                DeBERTa
                            </h2>

                        </div>

                    </div>

                    <ModelSection
                        data={statistics.deberta}
                    />

                </section>

            </div>


            {/* =========================================
                MODEL COMPARISON
            ========================================= */}

            <SectionCard title="Model Comparison">

                <div className="comparison-intro">

                    <Sparkles size={20} />

                    <p>
                        Agreement between the two analysis
                        approaches across sentiment and themes.
                    </p>

                </div>

                <ComparisonSection
                    comparison={statistics.comparison}
                />

            </SectionCard>


            {/* =========================================
                PREDICTIONS
            ========================================= */}

            <SectionCard title="Review Predictions">

                <div className="section-intro">

                    <div>

                        <span className="section-kicker">
                            PREDICTION PREVIEW
                        </span>

                        <p>
                            A preview of the predictions generated
                            for the analyzed reviews.
                        </p>

                    </div>

                </div>

                <PredictionTable
                    data={response.preview}
                />

            </SectionCard>

        </main>

    );

}


export default Results;