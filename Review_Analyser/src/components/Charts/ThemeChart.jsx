import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid,
    ResponsiveContainer
} from "recharts";

import "./Charts.css";

function ThemeChart({ themeData }) {

    const chartData = Object.entries(themeData)
        .filter(([_, count]) => count > 0)
        .map(([theme, count]) => ({
            theme,
            count
        }))
        .sort((a, b) => b.count - a.count);

    // Keep both model charts the same height
    const chartHeight = 300;

    return (
        <div className="chart-container theme-chart">

            <ResponsiveContainer
                width="100%"
                height={chartHeight}
            >

                <BarChart
                    data={chartData}
                    layout="vertical"
                    margin={{
                        top: 5,
                        right: 35,
                        left: 85,
                        bottom: 5
                    }}
                >

                    <CartesianGrid
                        strokeDasharray="3 3"
                        horizontal={false}
                    />

                    <XAxis
                        type="number"
                        allowDecimals={false}
                    />

                    <YAxis
                        type="category"
                        dataKey="theme"
                        width={85}
                        tick={{
                            fontSize: 11
                        }}
                    />

                    <Tooltip />

                    <Bar
                        dataKey="count"
                        fill="#2563EB"
                        radius={[0, 6, 6, 0]}
                    />

                </BarChart>

            </ResponsiveContainer>

        </div>
    );
}

export default ThemeChart;