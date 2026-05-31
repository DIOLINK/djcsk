module.exports = {
  content: [
    './pupistock/templates/**/*.html',
    './inventory/templates/**/*.html',
    './vistas/**/*.html',
  ],
  theme: {
    fontFamily: {
      sans: ['Manrope', 'sans-serif'],
    },
    extend: {
      colors: {
        // Adapta estos valores según tu paleta visual referenciada en ./vistas
        primary: '#BA905E',
        accent: '#E6C3A5',
        neutral: '#FFF9F2',
        dark: '#2E271B',
      },
    },
  },
  plugins: [],
};
