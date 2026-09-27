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
        darkbg: "#0B112C",
        sidebar: {
          DEFAULT: "#0B112C",
          dark: "#080D21",
          active: "#3B49DF",
          hover: "#151C3D",
        },
        brand: {
          blue: "#3B49DF",
          indigo: "#4F46E5",
          cyan: "#00D2FF",
          mint: "#10B981",
          lightBg: "#F4F7FC",
          card: "#FFFFFF",
          border: "#E2E8F0",
        },
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
          50: '#F8FAFC',
          100: '#F1F5F9',
          200: '#E2E8F0',
          300: '#CBD5E1',
          card: '#FFFFFF',
          border: '#E2E8F0',
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif'],
        display: ['Outfit', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        'brand-glow': '0 0 25px -4px rgba(59, 73, 223, 0.4)',
        'cyan-glow': '0 0 25px -4px rgba(0, 210, 255, 0.45)',
        'card-soft': '0 4px 20px -2px rgba(15, 23, 42, 0.05)',
        'card-hover': '0 12px 30px -4px rgba(15, 23, 42, 0.1)',
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
