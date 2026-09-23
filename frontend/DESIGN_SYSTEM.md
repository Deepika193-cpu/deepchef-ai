# DeepChef AI — Design System 

## Tokens (`tailwind.config.js`)
| Token | Value | Use |
|---|---|---|
| `primary` | `#FF6B35` | CTAs, active states, brand accents |
| `secondary` | `#FFF5F0` | Soft backgrounds, upload zones |
| `accent` | `#2E7D32` | Positive/health indicators, success states |
| `surface.bg` | `#F8FAFC` | Page background |
| `surface.card` | `#FFFFFF` | Card backgrounds |
| `ink.900/600/400` | grays | Primary / secondary / muted text |
| radius `card` | `16px` | All cards, inputs, upload zones |
| shadow `soft` / `softer` / `lift` | — | Resting / hover / emphasized elevation |

Fonts: **Poppins** for headings (`font-display`), **Inter** for body (`font-sans`), loaded via Google Fonts in `src/styles/index.css`.

## Components built (`src/components/`)
- **Button** — primary/secondary/outline/ghost/danger variants, loading + icon support
- **Card** — base surface with optional hover elevation
- **ProgressBar** — used for confidence scores, macro goals, water intake
- **States.jsx** — `LoadingState`, `SkeletonCard`, `EmptyState`, `ErrorMessage` (every screen must use these instead of a blank pane or raw error)
- **UploadBox** — drag-and-drop + browse, client-side validation (type, 10MB size cap), preview, remove
- **Layout.jsx** — `Navbar` (desktop) and `MobileTabBar` (mobile), same 5 sections: Analyze, Dashboard, History, Meal Planner, Profile


