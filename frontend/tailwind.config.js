/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        darkbg: "#060907",
        gold: {
          50: '#fdfbf0',
          100: '#f8f4db',
          200: '#f1e6b3',
          300: '#e7d485',
          400: '#dcb84f',
          500: '#d4af37',
          600: '#b89028',
          700: '#936e22',
          800: '#795722',
          900: '#674822',
        },
        surface: {
          50: '#0d120f',
          100: '#131a15',
          200: '#1b241e',
          300: '#232f27',
          card: 'rgba(19, 26, 21, 0.85)',
          border: 'rgba(212, 175, 55, 0.18)',
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
        display: ['Outfit', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        'gold-glow': '0 0 25px -4px rgba(212, 175, 55, 0.35)',
        'emerald-glow': '0 0 25px -4px rgba(16, 185, 129, 0.35)',
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      }
    },
  },
  plugins: [],
}
