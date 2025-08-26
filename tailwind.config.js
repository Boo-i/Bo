/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bright-orange': '#FF6B35',
        'bright-blue': '#4A90E2',
        'bright-yellow': '#FFD93D',
        'bright-green': '#6BCF7F',
        'bright-purple': '#9B59B6',
        'bright-pink': '#E91E63',
      },
      fontFamily: {
        'arabic': ['Tajawal', 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

