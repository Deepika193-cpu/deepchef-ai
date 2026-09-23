/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#FF6B35',
          hover: '#E85A2A',
          light: '#FFE4D9',
        },
        secondary: '#FFF5F0',
        accent: {
          DEFAULT: '#2E7D32',
          light: '#E8F5E9',
        },
        surface: {
          bg: '#F8FAFC',
          card: '#FFFFFF',
        },
        ink: {
          900: '#1A202C',
          600: '#4A5568',
          400: '#94A3B8',
        },
        danger: '#DC2626',
        warning: '#D97706',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['Poppins', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        card: '16px',
      },
      boxShadow: {
        soft: '0 2px 8px rgba(26, 32, 44, 0.06)',
        softer: '0 4px 16px rgba(26, 32, 44, 0.08)',
        lift: '0 8px 24px rgba(255, 107, 53, 0.15)',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
        'fade-in': {
          '0%': { opacity: 0, transform: 'translateY(4px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
      },
      animation: {
        shimmer: 'shimmer 2s infinite linear',
        'fade-in': 'fade-in 0.2s ease-out',
      },
    },
  },
  plugins: [],
};
