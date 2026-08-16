import "./Dashboard.css";

function PriorityIssues({ issues }) {

    if (!issues || issues.length === 0) {
        return (
            <div className="priority-section">

                <h3>Priority Issues</h3>

                <p>No issue data available.</p>

            </div>
        );
    }

    return (

        <div className="priority-section">

            <h3>Priority Issues</h3>

            <table className="priority-table">

                <thead>

                    <tr>

                        <th>Rank</th>
                        <th>Issue</th>
                        <th>Reviews</th>

                    </tr>

                </thead>

                <tbody>

                    {

                        issues.map((issue, index) => (

                            <tr key={index}>

                                <td>{index + 1}</td>

                                <td>{issue.theme}</td>

                                <td>{issue.count}</td>

                            </tr>

                        ))

                    }

                </tbody>

            </table>

        </div>

    );

}

export default PriorityIssues;