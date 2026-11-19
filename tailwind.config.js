/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './templates/**/*.html',
    './curriculum/templates/**/*.html',
    './jek_ia/templates/**/*.html',
    './proyectos/templates/**/*.html',
    './static/js/**/*.js',
    './curriculum/static/**/*.js',
    './jek_ia/static/**/*.js',
    './proyectos/static/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        accent: {
          primary: '#22A6BF',
          hover: '#1B8599',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        heading: ['Space Grotesk', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
