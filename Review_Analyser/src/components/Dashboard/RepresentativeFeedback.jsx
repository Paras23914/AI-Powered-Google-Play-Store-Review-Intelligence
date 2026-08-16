import "./Dashboard.css";

function RepresentativeFeedback({ feedback }) {

    if (!feedback || feedback.length === 0) {

        return (

            <div className="feedback-section">

                <h3>Representative Feedback</h3>

                <p>No feedback available.</p>

            </div>

        );

    }

    return (

        <div className="feedback-section">

            <h3>Representative Feedback</h3>

            {

                feedback.map((item, index) => (

                    <div
                        className="feedback-card"
                        key={index}
                    >

                        <h4>{item.theme}</h4>

                        <p>{item.review}</p>

                        <small>

                            Rating: {item.rating}

                        </small>

                    </div>

                ))

            }

        </div>

    );

}

export default RepresentativeFeedback;