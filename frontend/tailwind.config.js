/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        /* solid tokens (no opacity slicing) */
        bg: "var(--bg)",
        surface: "var(--surface)",
        border: "var(--border)",
        text: "var(--text)",
        muted: "var(--muted)",

        /* colors with opacity support using rgb triples */
        primary: "rgb(var(--primary-rgb, 37 99 235) / <alpha-value>)",
        success: "rgb(var(--success-rgb, 22 163 74) / <alpha-value>)",
        warning: "rgb(var(--warning-rgb, 217 119 6) / <alpha-value>)",
        danger:  "rgb(var(--danger-rgb, 220 38 38) / <alpha-value>)",
      },

      fontFamily: {
        sans: "var(--font-sans)",
        mono: "var(--font-mono)",
      },

      fontSize: {
        "token-2xl": "var(--fs-2xl)",
        "token-xl":  "var(--fs-xl)",
        "token-lg":  "var(--fs-lg)",
        "token-md":  "var(--fs-md)",
        "token-sm":  "var(--fs-sm)",
        "token-xs":  "var(--fs-xs)",
      },

      borderRadius: {
        "token-sm": "var(--radius-sm)",
        "token-md": "var(--radius-md)",
        "token-lg": "var(--radius-lg)",
        "token-full": "var(--radius-full)",
      },

      spacing: {
        "token-1": "var(--sp-1)",
        "token-2": "var(--sp-2)",
        "token-3": "var(--sp-3)",
        "token-4": "var(--sp-4)",
        "token-5": "var(--sp-5)",
        "token-6": "var(--sp-6)",
      },

      boxShadow: {
        "token-sm": "var(--shadow-sm)",
        "token-md": "var(--shadow-md)",
        "token-lg": "var(--shadow-lg)",
      },

      transitionDuration: {
        fast: "var(--transition-fast)",
        base: "var(--transition-base)",
      },
    },
  },
  plugins: [],
}
