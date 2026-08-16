import InfoCard from "../Common/InfoCard";
import "./StatsCards.css";
import { Cpu } from "lucide-react";
function StatsCards({ dataset, performance }) {

    return (
        <div className="stats-container">

            <InfoCard
                icon="📄"
                title="Total Reviews"
                value={dataset.total_reviews}
            />

            <InfoCard
                icon="⭐"
                title="Average Rating"
                value={dataset.average_rating}
            />

            <InfoCard
                icon="⚡"
                title="Processing Time"
                value={`${performance.processing_time} sec`}
            />

            <InfoCard
                icon="🚀"
                title="Reviews / Second"
                value={performance.reviews_per_second}
            />

            <InfoCard
                icon={<Cpu size={28} />}
                title="Processing Device"
                value={performance.device}
                className="device-card"
            />

        </div>
    );
}

export default StatsCards;