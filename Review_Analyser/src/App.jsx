import { useEffect, useState } from "react";
import { Routes, Route } from "react-router-dom";
import QwenAnalysis from "./pages/QwenAnalysis";
import QwenResults from "./pages/QwenResults";
import Home from "./pages/Home";
import Analysis from "./pages/Analysis";
import Results from "./pages/Results";
import GeminiAnalysis from "./pages/GeminiAnalysis";
import GeminiResults from "./pages/GeminiResults";
import ThemeToggle from "./components/Common/ThemeToggle";
import LLMSelection from "./pages/LLMSelection";
function App() {

    const [theme, setTheme] = useState(
        localStorage.getItem("theme") || "light"
    );

    useEffect(() => {

        document.documentElement.setAttribute(
            "data-theme",
            theme
        );

    }, [theme]);

    return (

        <>

            <ThemeToggle
                theme={theme}
                setTheme={setTheme}
            />

            <Routes>

                <Route
                    path="/"
                    element={<Home />}
                />

                <Route
                    path="/analysis"
                    element={<Analysis />}
                />

                <Route
                    path="/results"
                    element={<Results />}
                />
                <Route
                    path="/qwen"
                    element={<QwenAnalysis />}
                />
                <Route
                    path="/qwen-results"
                    element={<QwenResults />}
                />
                <Route
                    path="/gemini"
                    element={<GeminiAnalysis />}
                />

                <Route
                    path="/gemini-results"
                    element={<GeminiResults />}
                />
                <Route
                    path="/llm-selection"
                    element={<LLMSelection />}
                />
            </Routes>

        </>

    );

}

export default App;