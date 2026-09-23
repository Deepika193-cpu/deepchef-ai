import { useState } from 'react';

const NAV_ITEMS = [
  { key: 'home', label: 'Analyze' },
  { key: 'dashboard', label: 'Dashboard' },
  { key: 'history', label: 'History' },
  { key: 'favorites', label: 'Favorites' },
  { key: 'planner', label: 'Meal Planner' },
  { key: 'profile', label: 'Profile' },
];

export function Navbar({ active, onNavigate }) {
  return (
    <header className="sticky top-0 z-20 bg-surface-card/90 backdrop-blur border-b border-slate-100">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center text-white font-display font-semibold text-sm">
            DC
          </span>
          <span className="font-display font-semibold text-ink-900">DeepChef AI</span>
        </div>
        <nav className="hidden md:flex items-center gap-1">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.key}
              onClick={() => onNavigate(item.key)}
              className={`px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                active === item.key
                  ? 'text-primary bg-primary-light'
                  : 'text-ink-600 hover:text-ink-900 hover:bg-slate-50'
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </div>
    </header>
  );
}

export function MobileTabBar({ active, onNavigate }) {
  return (
    <nav className="md:hidden fixed bottom-0 inset-x-0 z-20 bg-surface-card border-t border-slate-100 flex overflow-x-auto py-2">
      {NAV_ITEMS.map((item) => (
        <button
          key={item.key}
          onClick={() => onNavigate(item.key)}
          className={`flex flex-col items-center gap-0.5 px-3 py-1 text-xs font-medium shrink-0 min-w-[64px] ${
            active === item.key ? 'text-primary' : 'text-ink-400'
          }`}
        >
          <span className={`h-1.5 w-1.5 rounded-full ${active === item.key ? 'bg-primary' : 'bg-transparent'}`} />
          {item.label}
        </button>
      ))}
    </nav>
  );
}
