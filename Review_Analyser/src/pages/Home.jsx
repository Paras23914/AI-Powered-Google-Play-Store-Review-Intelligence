import {
    BarChart3,
    Brain,
    ArrowRight,
    Sparkles
} from "lucide-react";

import { useNavigate } from "react-router-dom";

function Home() {

    const navigate = useNavigate();

    return (

        <main className="landing-container">

            <section className="landing-hero">

                <span className="landing-badge">

                    <Sparkles size={15} />

                    AI-Powered Review Intelligence

                </span>

                <h1>

                    Turn Reviews Into
                    <span> Insights.</span>

                </h1>

                <p>

                    Analyze Google Play Store reviews with
                    machine learning, transformer models,
                    and LLM-powered intelligence.

                </p>

            </section>


            <section className="analysis-selection">

                {/* =================================================
                    TRADITIONAL ML + DEBERTA
                ================================================= */}

                <article className="selection-card">

                    <div className="selection-icon">

                        <BarChart3 size={30} />

                    </div>

                    <div className="selection-content">

                        <span className="selection-label">
                            Review Analysis
                        </span>

                        <h2>
                            Traditional ML + DeBERTa
                        </h2>

                        <p>

                            Analyze sentiment, themes, and
                            priority issues using classical
                            machine learning alongside
                            transformer-based analysis.

                        </p>

                        <div className="selection-tags">

                            <span>Sentiment</span>
                            <span>Themes</span>
                            <span>Priority Issues</span>

                        </div>

                        <button
                            onClick={() => navigate("/analysis")}
                        >

                            Start Analysis

                            <ArrowRight size={18} />

                        </button>

                    </div>

                </article>


                {/* =================================================
                    LLM ANALYSIS
                ================================================= */}

                <article className="selection-card llm-selection">

                    <div className="selection-icon">

                        <Brain size={30} />

                    </div>

                    <div className="selection-content">

                        <span className="selection-label">
                            Advanced Intelligence
                        </span>

                        <h2>
                            LLM Analysis
                        </h2>

                        <p>

                            Generate deeper natural-language
                            insights, summaries, reasoning,
                            and intelligent review analysis
                            using your choice of LLM.

                        </p>

                        <div className="selection-tags llm-tags">

                            <span>Qwen</span>
                            <span>Gemini</span>
                            <span>Insights</span>

                        </div>

                        <button
                            onClick={() => navigate("/llm-selection")}
                        >

                            Choose LLM

                            <ArrowRight size={18} />

                        </button>

                    </div>

                </article>

            </section>


            <section className="landing-tech">

                <span>POWERED BY</span>

                <div>

                    <strong>Machine Learning</strong>

                    <i>•</i>

                    <strong>DeBERTa</strong>

                    <i>•</i>

                    <strong>Qwen</strong>

                    <i>•</i>

                    <strong>Google Gemini</strong>

                </div>

            </section>


            <p className="landing-footer">

                Choose between local and online AI analysis
                for deeper review intelligence.

            </p>

        </main>

    );

}

export default Home;