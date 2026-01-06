import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import enTranslations from './locales/en.json';
import heTranslations from './locales/he.json';
import arTranslations from './locales/ar.json';
import ruTranslations from './locales/ru.json';

// Get saved language from localStorage or default to English
const getSavedLanguage = (): string => {
  const saved = localStorage.getItem('tama38_language');
  if (saved && ['en', 'he', 'ar', 'ru'].includes(saved)) {
    return saved;
  }
  // Try to detect from browser
  const browserLang = navigator.language.split('-')[0];
  if (['en', 'he', 'ar', 'ru'].includes(browserLang)) {
    return browserLang;
  }
  return 'en';
};

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: {
        translation: enTranslations,
      },
      he: {
        translation: heTranslations,
      },
      ar: {
        translation: arTranslations,
      },
      ru: {
        translation: ruTranslations,
      },
    },
    lng: getSavedLanguage(),
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false, // React already escapes values
    },
    react: {
      useSuspense: false, // Disable suspense for better compatibility
    },
  });

// Update document direction based on language
const updateDocumentDirection = (lang: string) => {
  const isRTL = ['he', 'ar'].includes(lang);
  document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
  document.documentElement.lang = lang;
};

// Set initial direction
updateDocumentDirection(i18n.language);

// Update direction when language changes
i18n.on('languageChanged', (lng) => {
  updateDocumentDirection(lng);
  localStorage.setItem('tama38_language', lng);
});

export default i18n;

