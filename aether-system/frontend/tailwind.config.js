/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1a237e',
        accent: '#00bcd4',
        success: '#4caf50',
        warning: '#ff9800',
        error: '#f44336',
        'bg-dark': '#0a0e27',
        'bg-card': '#111936',
        'text-primary': '#ffffff',
        'text-secondary': '#94a3b8',
        border: '#1e293b',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
