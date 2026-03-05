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
        "bg-primary": "#1c1a1f",
        "bg-card-dark": "#1a1f1a",
        "bg-card-green": "#2c3833",
        "accent-sage": "#84a584",
        "text-cream": "#f9f5df",
        "text-light": "#f2f5f9",
        "text-muted": "#5d6a85",
        "text-dark": "#1c1a1a",
        "border-gray": "#cecece",
        "bg-light": "#eeeeee",
        olive: "#898a7d",
      },
      fontFamily: {
        display: ["var(--font-montserrat)", "system-ui", "sans-serif"],
        body: ["var(--font-plus-jakarta)", "system-ui", "sans-serif"],
        heading: ["var(--font-raleway)", "system-ui", "sans-serif"],
      },
      borderRadius: {
        "2xl": "16px",
        "3xl": "24px",
        "4xl": "32px",
        pill: "60px",
      },
    },
  },
  plugins: [],
};

export default config;
