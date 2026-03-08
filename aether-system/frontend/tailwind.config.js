/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#141414',
        accent: '#f59e0b',
        success: '#22c55e',
        warning: '#f59e0b',
        error: '#ef4444',
        'bg-dark': '#050505',
        'bg-card': '#0d0d0d',
        'text-primary': '#f5f2e9',
        'text-secondary': '#9a958a',
        border: '#333333',
      },
      fontFamily: {
        sans: ['Space Grotesk', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['IBM Plex Mono', 'ui-monospace', 'monospace'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
