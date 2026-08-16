import { Moon, Sun } from "lucide-react";

function ThemeToggle({ theme, setTheme }) {

    const toggleTheme = () => {

        const newTheme =
            theme === "light"
                ? "dark"
                : "light";

        setTheme(newTheme);

        localStorage.setItem(
            "theme",
            newTheme
        );

    };

    return (

        <button
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label="Toggle theme"
            title={
                theme === "light"
                    ? "Switch to dark mode"
                    : "Switch to light mode"
            }
        >

            {theme === "light" ? (
                <Moon size={20} />
            ) : (
                <Sun size={20} />
            )}

        </button>

    );

}

export default ThemeToggle;