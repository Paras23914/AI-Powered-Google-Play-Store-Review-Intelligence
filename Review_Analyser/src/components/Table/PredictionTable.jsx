import Badge from "../Common/Badge";
import "./PredictionTable.css";

function PredictionTable({ data }) {

    if (!data || data.length === 0) {
        return (
            <div className="prediction-table-container">
                <p className="no-predictions">
                    No prediction data available.
                </p>
            </div>
        );
    }

    return (
        <div className="prediction-table-container">

            <div className="table-wrapper">

                <table className="prediction-table">

                    <thead>
                        <tr>
                            <th className="rating-header">Rating</th>
                            <th className="review-header">Review</th>
                            <th>Traditional Sentiment</th>
                            <th>Traditional Theme</th>
                            <th>DeBERTa Sentiment</th>
                            <th>DeBERTa Theme</th>
                        </tr>
                    </thead>

                    <tbody>

                        {data.map((row, index) => {

                            const review = row.content || "";

                            return (
                                <tr key={index}>

                                    <td className="rating-cell">
                                        <span className="rating-value">
                                            {row.rating}
                                        </span>
                                    </td>

                                    <td
                                        className="review-column"
                                        title={review}
                                    >
                                        {review.length > 90
                                            ? review.substring(0, 90) + "..."
                                            : review
                                        }
                                    </td>

                                    <td>
                                        <Badge
                                            text={row.ml_sentiment}
                                            type={row.ml_sentiment.toLowerCase()}
                                        />
                                    </td>

                                    <td className="theme-cell">
                                        {row.ml_theme}
                                    </td>

                                    <td>
                                        <Badge
                                            text={row.bert_sentiment}
                                            type={row.bert_sentiment.toLowerCase()}
                                        />
                                    </td>

                                    <td className="theme-cell">
                                        {row.bert_theme}
                                    </td>

                                </tr>
                            );
                        })}

                    </tbody>

                </table>

            </div>

        </div>
    );
}

export default PredictionTable;