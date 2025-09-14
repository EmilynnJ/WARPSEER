import i18n from 'sveltekit-i18n';
import lang_en from './locales/en.json';
import lang_es from './locales/es.json';

export const { t, locale, locales, loading, setLocale } = i18n({
  loaders: [
    { locale: 'en', key: 'common', loader: async () => lang_en },
    { locale: 'es', key: 'common', loader: async () => lang_es }
  ],
  fallbackLocale: 'en'
});