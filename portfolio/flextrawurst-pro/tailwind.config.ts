import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg:      "#050810",
        bg2:     "#0a1020",
        bg3:     "#0f1830",
        border:  "#1a2840",
        text:    "#8899aa",
        text2:   "#b8c8d8",
        text3:   "#d8e8f0",
        accent:  "#3a6a9a",
        accent2: "#4a8abb",
        dim:     "#2a3a4a",
        ftw: {
          green: "#2a6a4a",
          red:   "#6a2a3a",
        },
      },
      fontFamily: {
        mono: ["JetBrains Mono", "Fira Mono", "Cascadia Code", "monospace"],
      },
      fontSize: {
        xs:  ["10px", "1.4"],
        sm:  ["11px", "1.5"],
        base:["13px", "1.6"],
        lg:  ["14px", "1.5"],
        xl:  ["16px", "1.4"],
      },
    },
  },
  plugins: [],
};

export default config;
