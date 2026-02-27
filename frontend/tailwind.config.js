/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          900: '#0F2444',
          800: '#163562',
          700: '#1A4080',
          500: '#2563EB',
          100: '#DBEAFE',
        },
        ink: {
          950: '#0C111D',
          900: '#111827',
          800: '#1F2937',
          700: '#374151',
          600: '#4B5563',
        },
        gold: {
          900: '#2A1F08',
          500: '#D4A843',
          400: '#E2C062',
          300: '#EDD38A',
        },
        parchment: '#F5EDD6',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
        display: ['Playfair Display', 'Georgia', 'serif'],
      },
      keyframes: {
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'glow-pulse': {
          '0%, 100%': { boxShadow: '0 0 6px rgba(212,168,67,0.4)' },
          '50%': { boxShadow: '0 0 14px rgba(212,168,67,0.8)' },
        },
        'dot-pulse': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.4' },
        },
      },
      animation: {
        'fade-up': 'fade-up 0.4s ease-out forwards',
        'fade-up-d1': 'fade-up 0.4s 0.1s ease-out forwards',
        'fade-up-d2': 'fade-up 0.4s 0.2s ease-out forwards',
        'fade-up-d3': 'fade-up 0.4s 0.3s ease-out forwards',
        'glow-pulse': 'glow-pulse 2s ease-in-out infinite',
        'dot-pulse': 'dot-pulse 1.5s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
