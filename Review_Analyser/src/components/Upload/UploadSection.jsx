import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { uploadCSV } from "../../services/api";

import LoadingScreen from "../Loading/LoadingScreen";

import "./UploadSection.css";


function UploadSection() {

    const navigate = useNavigate();

    const [selectedFile, setSelectedFile] = useState(null);

    const [isLoading, setIsLoading] = useState(false);

    const [error, setError] = useState("");

    const fileInputRef = useRef(null);


    const handleChooseFile = () => {

        fileInputRef.current.click();

    };


    const handleFileChange = (event) => {

        const file = event.target.files[0];

        if (!file) return;

        setError("");

        setSelectedFile(file);

    };


    const handleAnalyze = async () => {

        if (!selectedFile) return;

        try {

            setError("");

            setIsLoading(true);

            const response = await uploadCSV(selectedFile);

            navigate("/results", {
                state: response
            });

        }

        catch (error) {

            console.error(error);

            const backendMessage =
                error?.response?.data?.error;

            setError(
                backendMessage ||
                "Unable to analyze the file. Please try again."
            );

            setIsLoading(false);

        }

    };


    if (isLoading) {

        return <LoadingScreen />;

    }


    return (

        <div className="upload-container">

            <input
                type="file"
                accept=".csv"
                ref={fileInputRef}
                onChange={handleFileChange}
                style={{ display: "none" }}
            />


            <button
                className="upload-button"
                onClick={handleChooseFile}
            >

                📁 Choose CSV

            </button>


            {

                selectedFile ? (

                    <p className="selected-file">

                        📄 {selectedFile.name}

                    </p>

                ) : (

                    <p className="selected-file">

                        No file selected.

                    </p>

                )

            }


            {

                error && (

                    <div className="upload-error">

                        <span className="upload-error-icon">
                            ⚠️
                        </span>

                        <div>

                            <strong>
                                Unable to analyze dataset
                            </strong>

                            <p>
                                {error}
                            </p>

                        </div>

                    </div>

                )

            }


            <button
                className="analyze-button"
                onClick={handleAnalyze}
                disabled={!selectedFile}
            >

                🚀 Analyze Reviews

            </button>


            <div className="upload-requirements">

                <span>
                    CSV requirements
                </span>

                <ul>

                    <li>
                        File must be in CSV format
                    </li>

                    <li>
                        Required columns:
                        <strong> rating </strong>
                        and
                        <strong> content</strong>
                    </li>

                    <li>
                        Required columns must not contain empty values
                    </li>

                </ul>

            </div>

        </div>

    );

}


export default UploadSection;