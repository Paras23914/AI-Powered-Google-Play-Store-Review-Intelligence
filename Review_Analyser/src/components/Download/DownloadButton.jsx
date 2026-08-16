import "./Download.css";

function DownloadButton({ fileId }) {

    const handleDownload = () => {

        window.open(
            `http://127.0.0.1:8000/download/${fileId}`,
            "_blank"
        );

    };

    return (

        <div className="download-container">

            <button
                className="download-button"
                onClick={handleDownload}
            >

                ⬇ Download Results CSV

            </button>

        </div>

    );

}

export default DownloadButton;