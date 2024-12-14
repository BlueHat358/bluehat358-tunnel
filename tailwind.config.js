/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: "#0D1117", // Background
          text: "#E5E5E5", // Teks utama
        },
        cold: {
          primary: "#3B82F6", // Biru (Primary)
          accent: "#38BDF8", // Cyan (Accent)
        },
      },
    },
  },
  plugins: [],
};
