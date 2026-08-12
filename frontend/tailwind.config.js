/** @type {import('tailwindcss').Config} */
export default {
    content: ["./index.html", "./src/**/*.{js,jsx}"],
    theme: {
        extend: {
            colors: {
                ink: "#0a0a0a",
                paper: "#fbfaf7",
                accent: {
                    DEFAULT: "#ffde59",
                    dark: "#f5c400",
                },
                success: "#16a34a",
                danger: "#dc2626",
            },
            boxShadow: {
                hard: "6px 6px 0 0 #0a0a0a",
                "hard-sm": "3px 3px 0 0 #0a0a0a",
                "hard-lg": "10px 10px 0 0 #0a0a0a",
            },
            fontFamily: {
                sans: [
                    "Inter",
                    "ui-sans-serif",
                    "system-ui",
                    "-apple-system",
                    "sans-serif",
                ],
                mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
            },
        },
    },
    plugins: [],
};