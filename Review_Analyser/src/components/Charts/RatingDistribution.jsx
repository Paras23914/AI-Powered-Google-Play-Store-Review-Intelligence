import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from "recharts";

import "./Charts.css";

function RatingDistribution({ ratingData }) {

    const chartData = Object.entries(ratingData).map(
        ([rating, reviews]) => ({
            rating: `${rating}★`,
            reviews
        })
    );

    const totalReviews = Object.values(ratingData)
        .reduce((sum, value) => sum + value, 0);

    return (

        <div className="rating-overview">

            <div className="rating-chart">

                <ResponsiveContainer
                    width="100%"
                    height={280}
                >

                    <BarChart
                        data={chartData}
                        margin={{
                            top: 10,
                            right: 20,
                            left: 0,
                            bottom: 5
                        }}
                    >

                        <CartesianGrid
                            strokeDasharray="3 3"
                        />

                        <XAxis
                            dataKey="rating"
                        />

                        <YAxis />

                        <Tooltip />

                        <Bar
                            dataKey="reviews"
                            fill="#2563EB"
                            radius={[8, 8, 0, 0]}
                        />

                    </BarChart>

                </ResponsiveContainer>

            </div>


            <div className="rating-breakdown">

                <div className="rating-breakdown-header">

                    <h3>Rating Breakdown</h3>

                    <span>
                        {totalReviews} reviews
                    </span>

                </div>

                {

                    [...chartData].reverse().map((item) => {

                        const percentage =
                            totalReviews > 0
                                ? (
                                    item.reviews /
                                    totalReviews
                                ) * 100
                                : 0;

                        return (

                            <div
                                className="rating-row"
                                key={item.rating}
                            >

                                <span className="rating-label">
                                    {item.rating}
                                </span>

                                <div className="rating-progress">

                                    <div
                                        className="rating-progress-fill"
                                        style={{
                                            width:
                                                `${percentage}%`
                                        }}
                                    />

                                </div>

                                <span className="rating-count">
                                    {item.reviews}
                                </span>

                            </div>

                        );

                    })

                }

            </div>

        </div>

    );

}

export default RatingDistribution;