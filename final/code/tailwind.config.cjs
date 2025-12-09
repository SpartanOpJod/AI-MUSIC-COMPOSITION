// tailwind.config.cjs
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}"
  ],
  theme: {
    extend: {
      colors: {
        primary: "#1DB954",   // Spotify green
        secondary: "#0d1117", // dark background
        accent: "#00bcd4"     // blue accent
      },
      fontFamily: {
        sans: ["Poppins", "Inter", "sans-serif"]
      }
    }
  },
  plugins: [],
}
