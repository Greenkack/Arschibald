/**
 * i18n Configuration
 * Core internationalization setup using i18next
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

// Import translation files
import deTranslations from './locales/de.json';
import enTranslations from './locales/en.json';
import frTranslations from './locales/fr.json';
import esTranslations from './locales/es.json';
import itTranslations from './locales/it.json';
import plTranslations from './locales/pl.json';
import nlTranslations from './locales/nl.json';

export const supportedLanguages = {
  de: { name: 'Deutsch', nativeName: 'Deutsch', flag: '🇩🇪', rtl: false },
  en: { name: 'English', nativeName: 'English', flag: '🇬🇧', rtl: false },
  fr: { name: 'French', nativeName: 'Français', flag: '🇫🇷', rtl: false },
  es: { name: 'Spanish', nativeName: 'Español', flag: '🇪🇸', rtl: false },
  it: { name: 'Italian', nativeName: 'Italiano', flag: '🇮🇹', rtl: false },
  pl: { name: 'Polish', nativeName: 'Polski', flag: '🇵🇱', rtl: false },
  nl: { name: 'Dutch', nativeName: 'Nederlands', flag: '🇳🇱', rtl: false },
  ar: { name: 'Arabic', nativeName: 'العربية', flag: '🇸🇦', rtl: true },
  he: { name: 'Hebrew', nativeName: 'עברית', flag: '🇮🇱', rtl: true },
} as const;

export type SupportedLanguage = keyof typeof supportedLanguages;

const resources = {
  de: { translation: deTranslations },
  en: { translation: enTranslations },
  fr: { translation: frTranslations },
  es: { translation: esTranslations },
  it: { translation: itTranslations },
  pl: { translation: plTranslations },
  nl: { translation: nlTranslations },
};

i18n
  // Load translations from backend
  .use(Backend)
  // Detect user language
  .use(LanguageDetector)
  // Pass the i18n instance to react-i18next
  .use(initReactI18next)
  // Initialize i18next
  .init({
    resources,
    fallbackLng: 'de', // German as default
    defaultNS: 'translation',
    
    // Language detection options
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
      lookupLocalStorage: 'i18nextLng',
    },
    
    // Backend options for loading translations
    backend: {
      loadPath: '/api/v1/i18n/{{lng}}/{{ns}}',
      addPath: '/api/v1/i18n/{{lng}}/{{ns}}',
    },
    
    interpolation: {
      escapeValue: false, // React already escapes
      format: (value, format, lng) => {
        if (format === 'currency') {
          return new Intl.NumberFormat(lng, {
            style: 'currency',
            currency: 'EUR',
          }).format(value);
        }
        if (format === 'number') {
          return new Intl.NumberFormat(lng).format(value);
        }
        if (format === 'date') {
          return new Intl.DateTimeFormat(lng).format(new Date(value));
        }
        return value;
      },
    },
    
    react: {
      useSuspense: true,
      bindI18n: 'languageChanged loaded',
      bindI18nStore: 'added removed',
      transEmptyNodeValue: '',
      transSupportBasicHtmlNodes: true,
      transKeepBasicHtmlNodesFor: ['br', 'strong', 'i', 'p'],
    },
    
    // Debug mode (disable in production)
    debug: process.env.NODE_ENV === 'development',
    
    // Namespace separation
    ns: ['translation', 'common', 'errors', 'validation'],
    
    // Key separator
    keySeparator: '.',
    
    // Nesting separator
    nsSeparator: ':',
  });

export default i18n;
