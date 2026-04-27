import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ocean: {
          deep: "#0a2540",
          DEFAULT: "#1e4d8b",
          light: "#4a90d9",
        },
        hit: "#dc2626",
        sunk: "#7f1d1d",
        miss: "#94a3b8",
      },
    },
  },
  plugins: [],
};

export default config;
