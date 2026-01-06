import { useTranslation } from 'react-i18next';

const languages = [
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'he', name: 'עברית', flag: '🇮🇱' },
  { code: 'ar', name: 'العربية', flag: '🇸🇦' },
  { code: 'ru', name: 'Русский', flag: '🇷🇺' },
];

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const isRTL = ['he', 'ar'].includes(i18n.language);

  const changeLanguage = (langCode: string) => {
    i18n.changeLanguage(langCode);
  };

  return (
    <div className="relative group">
      <button className={`flex items-center px-3 py-2 text-sm text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors ${isRTL ? 'flex-row-reverse gap-2' : 'gap-2'}`}>
        <span className="text-lg">
          {languages.find((lang) => lang.code === i18n.language)?.flag || '🌐'}
        </span>
        <span className="hidden md:inline">
          {languages.find((lang) => lang.code === i18n.language)?.name || 'English'}
        </span>
        <svg
          className="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {/* Dropdown menu */}
      <div className={`absolute mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 ${isRTL ? 'left-0' : 'right-0'}`}>
        <div className="py-1">
          {languages.map((lang) => (
            <button
              key={lang.code}
              onClick={() => changeLanguage(lang.code)}
              className={`w-full flex items-center px-4 py-2 text-sm hover:bg-gray-50 transition-colors ${
                isRTL ? 'flex-row-reverse gap-3' : 'gap-3'
              } ${
                i18n.language === lang.code
                  ? 'bg-teal-50 text-teal-700 font-medium'
                  : 'text-gray-700'
              }`}
            >
              <span className="text-xl">{lang.flag}</span>
              <span className={isRTL ? 'text-right' : ''}>{lang.name}</span>
              {i18n.language === lang.code && (
                <span className={isRTL ? 'mr-auto text-teal-600' : 'ml-auto text-teal-600'}>✓</span>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

