/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#218090',
          light: '#32B8C6',
          dark: '#1a6370',
        },
        success: '#22C55E',
        warning: '#F59E0B',
        danger: '#EF4444',
        traffic: {
          green: '#10B981',
          yellow: '#F59E0B',
          red: '#EF4444',
        },
      },
    },
  },
  plugins: [],
}

