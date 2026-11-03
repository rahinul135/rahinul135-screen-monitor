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
          50: '#eef7f9',
          100: '#d9eef2',
          200: '#bfe0e9',
          300: '#8fc9dc',
          400: '#5fb4cf',
          500: '#2e4057',
          600: '#168aad',
          700: '#12708e',
          800: '#0d566b',
          900: '#0a4355',
        }
      }
    },
  },
  plugins: [],
}