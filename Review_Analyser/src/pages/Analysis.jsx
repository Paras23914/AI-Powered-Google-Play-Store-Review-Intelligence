import UploadSection from "../components/Upload/UploadSection";
import {
    Brain,
    BarChart3,
    Zap,
    FileSpreadsheet
} from "lucide-react";
import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";

function Analysis() {
    const navigate = useNavigate();
    return (

        <main className="home-container">
            <button
                className="page-back-button"
                onClick={() => navigate("/")}
            >
                <ArrowLeft size={17} />
                Back to Home
            </button>
            <section className="hero">

                <span className="hero-badge">
                    AI Powered Review Analytics
                </span>

                <h1 className="hero-title">
                    AI Review Intelligence
                </h1>

                <p className="hero-subtitle">
                    Transform thousands of Google Play Store reviews into
                    actionable insights using Traditional Machine Learning
                    and DeBERTa.
                </p>

            </section>

            <UploadSection />

            <section className="features">

                <div className="feature-card">

                    <Brain size={34} />

                    <h3>Sentiment Analysis</h3>

                    <p>
                        Detect positive, neutral and negative reviews.
                    </p>

                </div>

                <div className="feature-card">

                    <BarChart3 size={34} />

                    <h3>Theme Detection</h3>

                    <p>
                        Discover the most discussed customer issues.
                    </p>

                </div>

                <div className="feature-card">

                    <Zap size={34} />

                    <h3>Fast Processing</h3>

                    <p>
                        Analyze thousands of reviews in seconds.
                    </p>

                </div>

                <div className="feature-card">

                    <FileSpreadsheet size={34} />

                    <h3>CSV Export</h3>

                    <p>
                        Download complete prediction results instantly.
                    </p>

                </div>

            </section>

        </main>

    );

}

export default Analysis;