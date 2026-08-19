import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        accent: {
          DEFAULT: "#059669",
          foreground: "#ffffff",
        },
        surface: {
          DEFAULT: "#27272a",
          border: "#3f3f46",
          muted: "#71717a",
        },
      },
    },
  },
  plugins: [],
};

export default config;
