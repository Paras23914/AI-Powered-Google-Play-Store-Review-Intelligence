import "./Dashboard.css";

import SentimentChart from "../Charts/SentimentChart";
import ThemeChart from "../Charts/ThemeChart";
import PriorityIssues from "./PriorityIssues";

function ModelSection({ data }) {

    return (

        <div className="model-section">

            <div className="model-analysis-block">

                <h3 className="analysis-block-title">
                    Sentiment Analysis
                </h3>

                <SentimentChart
                    sentimentData={data.sentiment}
                />

            </div>


            <div className="model-analysis-block">

                <h3 className="analysis-block-title">
                    Theme Distribution
                </h3>

                <ThemeChart
                    themeData={data.theme}
                />

            </div>


            <div className="model-analysis-block">

                <PriorityIssues
                    issues={data.priority_issues}
                />

            </div>

        </div>

    );

}

export default ModelSection;