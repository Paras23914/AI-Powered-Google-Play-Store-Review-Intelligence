import axios from "axios";

const API = axios.create({
    baseURL: "http://127.0.0.1:8000",
});


// ============================================================
// EXISTING ML ANALYZER
// ============================================================

export const uploadCSV = async (file) => {

    const formData = new FormData();

    formData.append("file", file);

    const response = await API.post(
        "/analyze",
        formData,
        {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        }
    );

    return response.data;
};


// ============================================================
// START QWEN ANALYSIS
// ============================================================

export const uploadQwenCSV = async (file) => {

    const formData = new FormData();

    formData.append("file", file);

    const response = await API.post(
        "/analyze/qwen",
        formData,
        {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        }
    );

    return response.data;
};


// ============================================================
// START GEMINI ANALYSIS
// ============================================================

export const uploadGeminiCSV = async (file) => {

    const formData = new FormData();

    formData.append("file", file);

    const response = await API.post(
        "/analyze/gemini",
        formData,
        {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        }
    );

    return response.data;
};


// ============================================================
// GET ANALYSIS PROGRESS
// ============================================================

export const getAnalysisProgress = async (jobId) => {

    const response = await API.get(
        `/progress/${jobId}`
    );

    return response.data;
};


// ============================================================
// DOWNLOAD RESULT CSV
// ============================================================

export const downloadResult = async (fileId) => {

    const response = await API.get(
        `/download/${fileId}`,
        {
            responseType: "blob",
        }
    );

    const blob = new Blob(
        [response.data],
        {
            type: "text/csv",
        }
    );

    const url = window.URL.createObjectURL(
        blob
    );

    const link = document.createElement(
        "a"
    );

    link.href = url;

    link.download = "analysis_results.csv";

    document.body.appendChild(link);

    link.click();

    link.remove();

    window.URL.revokeObjectURL(url);
};