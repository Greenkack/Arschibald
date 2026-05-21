/**
 * PrimeReact Theme Configuration
 * 
 * This file configures the PrimeReact theme for the application.
 * It provides a centralized place to customize the look and feel.
 */

export const primeReactTheme = {
  // Use the default Lara theme (light mode)
  theme: 'lara-light-blue',
  
  // Custom CSS variables for theme customization
  cssVariables: {
    '--primary-color': '#2196F3',
    '--primary-color-text': '#ffffff',
    '--surface-0': '#ffffff',
    '--surface-50': '#fafafa',
    '--surface-100': '#f5f5f5',
    '--surface-200': '#eeeeee',
    '--surface-300': '#e0e0e0',
    '--surface-400': '#bdbdbd',
    '--surface-500': '#9e9e9e',
    '--surface-600': '#757575',
    '--surface-700': '#616161',
    '--surface-800': '#424242',
    '--surface-900': '#212121',
    '--text-color': '#212121',
    '--text-color-secondary': '#757575',
    '--border-radius': '6px',
  },
};

/**
 * Apply PrimeReact theme to the document
 */
export const applyPrimeReactTheme = () => {
  const root = document.documentElement;
  
  Object.entries(primeReactTheme.cssVariables).forEach(([key, value]) => {
    root.style.setProperty(key, value);
  });
};

/**
 * Load PrimeReact CSS
 */
export const loadPrimeReactCSS = () => {
  // PrimeReact core CSS
  import('primereact/resources/primereact.min.css');
  
  // PrimeReact theme CSS (Lara Light Blue)
  import('primereact/resources/themes/lara-light-blue/theme.css');
  
  // PrimeIcons
  import('primeicons/primeicons.css');
};
