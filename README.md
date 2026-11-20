# Hali University Wellbeing

Hali is a React + Vite + Bootstrap frontend and FastAPI service for university wellbeing. Student registration is open; counsellor registration requires a university invitation code. Both roles use the same sign-in page.

## Run locally

Run the backend and frontend in **two separate terminals** from the repository root.

1. In terminal 1, set up and start the API:

   ```sh
   cd hali-backend
   python3 -m venv .venv
   . .venv/bin/activate
   pip install -r requirements-dev.txt
   cp .env.example .env
   ```

   Edit `hali-backend/.env`: set `AUTH_SECRET_KEY` to a random secret (generate one with `openssl rand -hex 32`) and set `AUTH_COUNSELLOR_INVITE_CODE` if counsellor sign-up is needed. Then, in the same terminal:

   ```sh
   uvicorn app.main:app --env-file .env --reload
   ```

2. Open terminal 2 at the repository root, install frontend dependencies (first run only), and start the frontend:

   ```sh
   npm install
   npm run dev
   ```

   The Vite development server proxies `/api` requests to the local backend on port 8000. Open the local URL printed by Vite, usually `http://localhost:5173`. If the API is hosted elsewhere, set `VITE_API_BASE_URL` to its `/api` URL before starting Vite.

3. Run backend auth tests:

   ```sh
   cd hali-backend
   .venv/bin/python -m pytest tests
   ```

## Authentication

- Student and counsellor accounts are the only roles accepted by the public registration endpoint. Login role is determined by the server.
- Registration requires a unique username (3–32 letters or numbers, with dots, underscores or hyphens allowed between characters), university email, and password. Sign-in accepts either username or email plus password; usernames are case-insensitive.
- Student registration is open. Counsellor registration requires `AUTH_COUNSELLOR_INVITE_CODE`.
- Passwords use Argon2id hashes. Sessions use 12-hour HTTP-only cookies; credentials and session tokens are not stored in browser local storage.
- Email addresses are normalized, passwords must be at least 12 characters, and duplicate accounts are rejected.
- Existing accounts remain usable with email and password; they can continue to sign in by email.
- Optional research and re-contact consent selections are stored against the signed-in account.
- Production requires a random `AUTH_SECRET_KEY`, a non-SQLite database (for example, `postgresql+psycopg://...` in `DATABASE_URL`), `ENVIRONMENT=production`, HTTPS, and the correct frontend origins in `ALLOWED_ORIGINS`. Never use the example invite code or a checked-in secret in a deployment.
- Before handling real users, configure email ownership verification, password recovery, and authentication rate-limiting at the API gateway.

## Product prototype scope

- Public: welcoming landing page with student community photography, secure sign-in, and six-step account creation with privacy and optional research consent. Student photos are served locally and credited to [Pexels](https://www.pexels.com/).
- Student: redesigned wellbeing dashboard, campus communities directory, mood and weekly check-ins, resources, counsellor booking, messaging, assistant, privacy centre, and help.
- Counsellor: overview, cases, risk monitoring, appointments, and messaging.
- Admin and researcher pages remain in the codebase but are not available through public account creation or sign-in.
- Student check-ins, counselling workflows, appointments, messages, analytics, and research views remain sample-data prototype features. Authentication and account storage are server-backed; the rest of the product services are not yet connected to production data. Do not use sample-data features for real health records or care decisions.
- The communities directory is a starter example, not an official university listing. Social buttons open public platform searches; they are not verified club accounts or social sign-in. Joining a group is saved only in the current browser and does not enroll or notify a real group. Replace the sample directory and links with university-verified details before launch.
- The project also includes a PWA manifest and build-generated service worker. It is registered only in production builds (`npm run build && npm run preview`).

## Structure

The frontend is organized into `components/`, `layouts/`, `pages/`, `services/`, `context/`, `hooks/`, `utils/`, and `data/`. The backend authentication service is in `hali-backend/app/`; it creates its initial tables at startup.
