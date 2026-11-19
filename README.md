# Hali frontend (demo)

React + Vite + Bootstrap 5 + Recharts frontend for Hali, a university mental wellness platform. Frontend only: all data is synthetic and served by mock services.

## Run
    npm install
    npm run dev      # http://localhost:5173
    npm run build    # production build in dist/
Copy `.env.example` to `.env` to set `VITE_API_BASE_URL`.

## Demo
Open `/#/login` and pick a role (no credentials). Suggested path: Student > Weekly check-in (answer "Several days" or higher) > Book a counsellor > Counsellor > open a case > Generate Case Brief > University Admin > Privacy rules.

## What is implemented
- Public: landing page, 6-step onboarding, role-select demo login, role switcher in the sidebar.
- Student: dashboard, mood check-in with history, weekly check-in (quick 5-question or full 21-question PHQ-9 + GAD-7 + WHO-5) with autosave and green/amber/red routing (any positive PHQ-9 item 9 answer goes to red with a human handoff panel), resources, calendar-based booking and cancellation, simulated messaging, EN/Kiswahili assistant with human handoff, privacy centre, 4-tier Get Help Now (placeholder, unverified contacts).
- Counsellor: overview with workload chart, cases, risk monitoring, case detail (score trends, timeline, sessions, notes, mock case brief), appointments in List/Day/Week/Month views, messaging.
- Admin: aggregate overview, 7 Recharts visualisations, cohort-size-10 suppression, management and audit log.
- Researcher: consent overview, aggregate stats, withdrawal history, draft dataset request UI.
- Structure follows the brief: `components/{common,cards,charts,forms,modals,navigation}`, `layouts/*Layout.jsx`, `pages/{public,student,counsellor,admin,researcher}`, `services/` (one module per API area), `hooks/`, `utils/`, `data/`. Routes are lazy-loaded.
- PWA: manifest, PNG/SVG icons, and a service worker generated at build time that precaches all built files. It is registered only in production builds (`npm run build && npm run preview`).

## Limits
Everything is synthetic demo data with no real verification, encryption or backend. Screening scores are shown as screening only. Video, exports and payments are intentionally not built. The service worker and layouts were checked by a build and a server-side render of every page, not in real browsers or on devices, so test installability and offline use yourself.

## Backend swap
All calls go through `src/services/api.js`; set `MOCK = false` and replace each mock with Axios calls. Demo state is stored in localStorage under `hali-demo-v1` (non-sensitive mock data only).
