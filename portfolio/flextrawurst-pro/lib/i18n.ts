"use client";

import React, { createContext, useContext, useState, useCallback } from "react";

type Lang = "de" | "en";

interface I18nContextType {
  lang: Lang;
  t: (key: string, fallback?: string) => string;
  setLang: (lang: Lang) => void;
}

const I18nContext = createContext<I18nContextType>({
  lang: "de",
  t: (key, fallback) => fallback ?? key,
  setLang: () => {},
});

export function I18nProvider({
  children,
  initialTranslations,
  initialLang = "de",
}: {
  children: React.ReactNode;
  initialTranslations: Record<string, string>;
  initialLang?: Lang;
}) {
  const [lang, setLangState] = useState<Lang>(initialLang);
  const [translations, setTranslations] = useState<Record<string, string>>(initialTranslations);

  const setLang = useCallback(async (newLang: Lang) => {
    try {
      const res = await fetch(`/i18n/${newLang}.json`);
      const tr = await res.json() as Record<string, string>;
      setTranslations(tr);
    } catch {}
    setLangState(newLang);
    if (typeof window !== "undefined") {
      localStorage.setItem("ftw_lang", newLang);
    }
  }, []);

  const t = useCallback(
    (key: string, fallback?: string): string => {
      return translations[key] ?? fallback ?? key;
    },
    [translations]
  );

  return React.createElement(
    I18nContext.Provider,
    { value: { lang, t, setLang } },
    children
  );
}

export function useI18n() {
  return useContext(I18nContext);
}
