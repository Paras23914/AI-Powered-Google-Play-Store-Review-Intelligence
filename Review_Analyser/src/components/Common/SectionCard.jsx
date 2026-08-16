import "./Common.css";
function SectionCard({ title, children }) {

    return (

        <section className="section-card">

            <h2>{title}</h2>

            {children}

        </section>

    );

}

export default SectionCard;