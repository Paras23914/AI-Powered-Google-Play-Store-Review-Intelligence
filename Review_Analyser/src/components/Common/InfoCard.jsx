import "./Common.css";

function InfoCard({
    title,
    value,
    icon,
    className = ""
}) {

    return (

        <div className={`info-card ${className}`}>

            <span>{icon}</span>

            <h4>{title}</h4>

            <h2>{value}</h2>

        </div>

    );

}

export default InfoCard;