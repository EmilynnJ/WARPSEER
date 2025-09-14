/**** Tailwind config for SoulSeer mystical theme ****/
const defaultTheme = require('tailwindcss/defaultTheme');

/**** Fonts will be loaded via @fontsource CDN in app template ****/

/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: ['./src/**/*.{svelte,ts}'],
  theme: {
    extend: {
      colors: {
        mystic: {
          pink: '#FF69B4',
          gold: '#C9A227',
          black: '#0B0B0F',
          white: '#FFFFFF'
        }
      },
      fontFamily: {
        script: ['"Alex Brush"', ...defaultTheme.fontFamily.serif],
        display: ['"Playfair Display"', ...defaultTheme.fontFamily.serif]
      }
    }
  },
  plugins: [require('tailwindcss-animate')]
};