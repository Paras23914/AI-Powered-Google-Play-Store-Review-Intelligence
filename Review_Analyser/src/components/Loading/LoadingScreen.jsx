import "./Loading.css";
import { Brain, Database, BarChart3, LoaderCircle } from "lucide-react";

function LoadingScreen() {

    return (

        <div className="loading-screen">

            <div className="loading-card">

                <div className="loading-icon">

                    <LoaderCircle size={32} />

                </div>

                <h1>
                    AI Review Intelligence
                </h1>

                <h2>
                    Analyzing Reviews...
                </h2>

                <p>
                    Your dataset is being processed.
                    Please wait while the analysis pipeline completes.
                </p>


                <div className="loading-steps">

                    <div className="loading-step">

                        <span className="step-icon">
                            <Database size={18} />
                        </span>

                        <span>
                            Dataset validation & preprocessing
                        </span>

                    </div>


                    <div className="loading-step">

                        <span className="step-icon">
                            <Brain size={18} />
                        </span>

                        <span>
                            Machine learning & DeBERTa analysis
                        </span>

                    </div>


                    <div className="loading-step">

                        <span className="step-icon">
                            <BarChart3 size={18} />
                        </span>

                        <span>
                            Generating analysis statistics
                        </span>

                    </div>

                </div>

            </div>

        </div>

    );

}

export default LoadingScreen;