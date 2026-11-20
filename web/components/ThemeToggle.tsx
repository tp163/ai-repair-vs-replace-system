'use client';

import { useSyncExternalStore } from 'react';
import { Moon, Sun } from 'lucide-react';

const THEME_KEY = 'revivai-theme';

function subscribe(onChange: () => void) {
  const onStorage = (event: StorageEvent) => {
    if (event.key !== THEME_KEY && event.key !== null) return;
    document.documentElement.dataset.theme = event.newValue === 'light' ? 'light' : 'dark';
    onChange();
  };
  window.addEventListener('revivai-theme-change', onChange);
  window.addEventListener('storage', onStorage);
  return () => {
    window.removeEventListener('revivai-theme-change', onChange);
    window.removeEventListener('storage', onStorage);
  };
}

export default function ThemeToggle() {
  const theme = useSyncExternalStore(
    subscribe,
    () => document.documentElement.dataset.theme === 'light' ? 'light' : 'dark',
    () => 'dark',
  );
  const isLight = theme === 'light';

  function toggleTheme() {
    const next = isLight ? 'dark' : 'light';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem(THEME_KEY, next); } catch { /* Works without storage. */ }
    window.dispatchEvent(new Event('revivai-theme-change'));
  }

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="theme-toggle"
      aria-label={`Switch to ${isLight ? 'dark' : 'light'} theme`}
      aria-pressed={isLight}
      title={`Switch to ${isLight ? 'dark' : 'light'} theme`}
    >
      {isLight ? <Sun size={16} aria-hidden="true" /> : <Moon size={16} aria-hidden="true" />}
      <span className="hidden sm:inline">{isLight ? 'Light' : 'Dark'}</span>
    </button>
  );
}
