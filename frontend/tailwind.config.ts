import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        marina: {
          50: "#eef5ff",
          100: "#d9e8ff",
          200: "#bcd7ff",
          300: "#8ebdff",
          400: "#5999ff",
          500: "#3273fc",
          600: "#1a53f0",
          700: "#143edc",
          800: "#003399", // Chennaiyin FC Marina Blue
          900: "#122d86",
          950: "#0a194e",
        },
      },
    },
  },
  plugins: [],
};

export default config;
