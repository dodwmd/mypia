/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      "./app/**/*.{js,ts,jsx,tsx}",
      "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
      extend: {
        colors: {
          primary: {
            DEFAULT: '#4A148C',
            light: '#7C43BD',
            dark: '#12005E',
          },
          secondary: {
            DEFAULT: '#00796B',
            light: '#48A999',
            dark: '#004C40',
          },
          accent: {
            DEFAULT: '#FFA000',
            light: '#FFC947',
            dark: '#C67100',
          },
          background: '#F5F7FA',
          text: '#333333',
        },
      },
    },
    plugins: [],
  }
