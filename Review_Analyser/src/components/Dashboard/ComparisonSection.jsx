import "./Dashboard.css";

function ComparisonSection({ comparison }) {

    return (
        <div className="comparison-section">

            <div className="comparison-grid">

                <div className="comparison-card">

                    <div className="comparison-card-top">
                        <span>Sentiment Agreement</span>

                        <strong>
                            {comparison.sentiment_agreement}%
                        </strong>
                    </div>

                    <div className="comparison-progress">
                        <div
                            className="comparison-progress-fill"
                            style={{
                                width: `${comparison.sentiment_agreement}%`
                            }}
                        />
                    </div>

                    <small>
                        Prediction agreement
                    </small>

                </div>


                <div className="comparison-card">

                    <div className="comparison-card-top">
                        <span>Theme Agreement</span>

                        <strong>
                            {comparison.theme_agreement}%
                        </strong>
                    </div>

                    <div className="comparison-progress">
                        <div
                            className="comparison-progress-fill"
                            style={{
                                width: `${comparison.theme_agreement}%`
                            }}
                        />
                    </div>

                    <small>
                        Prediction agreement
                    </small>

                </div>

            </div>

        </div>
    );
}

export default ComparisonSection;