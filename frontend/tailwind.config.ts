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
        // MARINA INTELLIGENCE — Light Football Performance Palette
        pitch: {
          white: "#FFFFFF",
          mist: "#F4F8F4",
          soft: "#E6F0E7",
          green: "#246B45",
          dark: "#174B32",
          charcoal: "#26332B",
          muted: "#718078",
          border: "#E2EAE3",
          warning: "#D9A441",
          negative: "#C65B56",
        },
        cfc: {
          blue: "#003399", // Chennaiyin FC Official Primary
          gold: "#FFB81C", // Official Gold Accent
          sky: "#E8F0FE",
        },
      },
    },
  },
  plugins: [],
};

export default config;
