"use client";

import { createContext, useContext, useEffect, useState } from "react";

type Theme = "light" | "dark" | "system";

const ThemeContext = createContext<{
  theme: Theme;
  isDark: boolean;
  setTheme: (theme: Theme) => void;
}>({ theme: "system", isDark: false, setTheme: () => {} });

export function useTheme() {
  return useContext(ThemeContext);
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>("system");
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("theme") as Theme | null;
    if (stored) setTheme(stored);
  }, []);

  useEffect(() => {
    const root = document.documentElement;
    let dark: boolean;
    if (theme === "system") {
      dark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    } else {
      dark = theme === "dark";
    }
    root.classList.toggle("dark", dark);
    setIsDark(dark);
    localStorage.setItem("theme", theme);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, isDark, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
