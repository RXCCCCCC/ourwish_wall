/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'brand-red': '#E60012',
        'brand-dark': '#0F172A',
      },
      fontFamily: {
        serif: ['SimSun', 'Songti SC', 'serif'],
        sans: ['PingFang SC', 'Microsoft YaHei', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
