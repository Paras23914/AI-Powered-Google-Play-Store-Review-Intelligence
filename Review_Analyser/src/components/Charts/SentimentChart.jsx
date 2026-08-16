import {
    PieChart,
    Pie,
    Cell,
    Tooltip,
    Legend,
    ResponsiveContainer
} from "recharts";

import "./Charts.css";

const COLORS = [
    "#22C55E",
    "#EF4444",
    "#FACC15"
];

function SentimentChart({ sentimentData }) {

    const chartData = Object.entries(sentimentData).map(
        ([name, value]) => ({
            name,
            value
        })
    );

    return (

        <div className="chart-container">

            <ResponsiveContainer
                width="100%"
                height={300}
            >

                <PieChart>

                    <Pie
                        data={chartData}
                        dataKey="value"
                        nameKey="name"
                        outerRadius={100}
                        label
                    >

                        {

                            chartData.map((_, index) => (

                                <Cell
                                    key={index}
                                    fill={
                                        COLORS[
                                            index % COLORS.length
                                        ]
                                    }
                                />

                            ))

                        }

                    </Pie>

                    <Tooltip />

                    <Legend />

                </PieChart>

            </ResponsiveContainer>

        </div>

    );

}

export default SentimentChart;