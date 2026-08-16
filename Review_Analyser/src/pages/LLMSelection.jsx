import {
    ArrowLeft,
    ArrowRight,
    Brain,
    Cloud,
    Cpu,
    Sparkles
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import "./LLMSelection.css";

function LLMSelection() {

    const navigate = useNavigate();

    return (

        <main className="llm-selection-page">

            {/* Navigation */}

            <button
                className="page-back-button"
                onClick={() => navigate("/")}
            >
                <ArrowLeft size={17} />
                Back to Home
            </button>


            {/* Header */}

            <section className="llm-selection-header">

                <span className="llm-selection-badge">
                    <Sparkles size={15} />
                    AI Review Intelligence
                </span>

                <h1>
                    Choose Your AI Model
                </h1>

                <p>
                    Select how you want your Google Play Store
                    reviews to be analyzed.
                </p>

            </section>


            {/* Model Cards */}

            <section className="llm-options">


                {/* QWEN */}

                <article className="llm-card qwen-card">

                    <div className="llm-card-icon">
                        <Cpu size={32} />
                    </div>

                    <span className="llm-card-label">
                        OFFLINE • LOCAL
                    </span>

                    <h2>
                        Qwen 3 8B
                    </h2>

                    <p>
                        Run the analysis locally using the
                        Qwen 3 8B model. Your review data
                        stays on your machine.
                    </p>

                    <div className="llm-features">

                        <span>
                            ✓ Local Processing
                        </span>

                        <span>
                            ✓ No Cloud API
                        </span>

                        <span>
                            ✓ Private Dataset
                        </span>

                    </div>

                    <button
                        className="llm-select-button qwen-button"
                        onClick={() => navigate("/qwen")}
                    >

                        Use Qwen

                        <ArrowRight size={18} />

                    </button>

                </article>


                {/* GEMINI */}

                <article className="llm-card gemini-card">

                    <div className="llm-card-icon">
                        <Cloud size={32} />
                    </div>

                    <span className="llm-card-label">
                        ONLINE • CLOUD
                    </span>

                    <h2>
                        Google Gemini
                    </h2>

                    <p>
                        Analyze your reviews using Google's
                        online Gemini API for fast,
                        cloud-based intelligence.
                    </p>

                    <div className="llm-features">

                        <span>
                            ✓ Online Gemini API
                        </span>

                        <span>
                            ✓ Fast Processing
                        </span>

                        <span>
                            ✓ Advanced AI Analysis
                        </span>

                    </div>

                    <button
                        className="llm-select-button gemini-button"
                        onClick={() => navigate("/gemini")}
                    >

                        Use Gemini

                        <ArrowRight size={18} />

                    </button>

                </article>

            </section>


            {/* Information */}

            <section className="llm-selection-info">

                <Brain size={20} />

                <div>

                    <strong>
                        What's the difference?
                    </strong>

                    <p>
                        Qwen runs locally on your computer,
                        while Gemini sends the analysis
                        through Google's online AI service.
                    </p>

                </div>

            </section>

        </main>

    );
}

export default LLMSelection;