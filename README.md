# Hali University Wellbeing

Hali is a React + Vite + Bootstrap frontend and FastAPI service for university wellbeing. Student registration is open; counsellor registration requires a university invitation code. Both roles use the same sign-in page.

## Run locally

The frontend and backend are maintained in separate repositories. Keep the two repositories side by side:

```text
wellness/
  hali-wellness/   # this frontend repository
  hali-backend/    # https://github.com/Cathy-matu/uhali-gani-b
```

Clone the backend once from the frontend repository root if you do not already have the sibling folder:

```sh
git clone https://github.com/Cathy-matu/uhali-gani-b.git ../hali-backend
```

Run the backend and frontend in **two separate terminals**.

1. In terminal 1, set up and start the API:

   ```sh
   cd ../hali-backend
   python3 -m venv .venv
   . .venv/bin/activate
   pip install -r requirements-dev.txt
   cp .env.example .env
   ```

   Edit `.env`: set `AUTH_SECRET_KEY` to a random secret (generate one with `openssl rand -hex 32`) and set `AUTH_COUNSELLOR_INVITE_CODE` if counsellor sign-up is needed. Then, in the same terminal, start the API with the local SQLite database and port 8001:

   ```sh
   DATABASE_URL=sqlite:///./hali.db uvicorn app.main:app --env-file .env --reload --port 8001
   ```

2. Open terminal 2 at the repository root, install frontend dependencies (first run only), and start the frontend:

   ```sh
   npm install
   npm run dev
   ```

   The Vite development server proxies `/api` requests to the Hali backend on port 8001. Open the local URL printed by Vite, usually `http://localhost:5173`. The checked-in `.env.example` uses this same-origin `/api` path. For a deployed frontend calling a separately hosted API directly, set `VITE_API_BASE_URL` to the backend's full `/api` URL before building/redeploying the frontend, and add the exact frontend origin to the backend's `ALLOWED_ORIGINS`. Auth uses an HTTP-only cookie; configure `AUTH_COOKIE_SAMESITE=none` on the backend only when the frontend and API are on different sites, and serve both over HTTPS. Same-site custom domains or a same-origin `/api` proxy are more reliable where browsers restrict third-party cookies.

3. Run backend auth tests from the frontend repository root:

   ```sh
   cd ../hali-backend
   .venv/bin/python -m pytest tests
   ```

## Authentication

- Student and counsellor accounts are the only roles accepted by the public registration endpoint. Login role is determined by the server.
- Registration requires a unique username (3–32 letters or numbers, with dots, underscores or hyphens allowed between characters), university email, and password. Sign-in accepts either username or email plus password; usernames are case-insensitive.
- Student registration is open. Counsellor registration requires `AUTH_COUNSELLOR_INVITE_CODE`.
- For counsellor registration, the invitation field must match the backend's `AUTH_COUNSELLOR_INVITE_CODE` (not `AUTH_SECRET_KEY`). Surrounding spaces are ignored; restart the backend after changing its `.env`. A `403` means the backend's configured code and submitted code do not match.
- Passwords use Argon2id hashes. Sessions use 12-hour HTTP-only cookies; credentials and session tokens are not stored in browser local storage.
- Sign-in and registration use browser-standard username/password autocomplete fields and offer to store credentials through the browser password manager where supported. The browser controls whether to show a save prompt; Hali never stores a plaintext password.
- Email addresses are normalized, passwords must be at least 12 characters, and duplicate accounts are rejected.
- Existing accounts remain usable with email and password; they can continue to sign in by email.
- Account registration stores the selected C2 research-consent flag and re-contact choice against the account; later C2 changes update the account flag. Longitudinal C1/C3 choices and consent history are browser-local, and no consent choice currently gates a live research data service.
- Production requires a random `AUTH_SECRET_KEY`, a non-SQLite database (for example, `postgresql+psycopg://...` in `DATABASE_URL`), `ENVIRONMENT=production`, HTTPS, and the correct frontend origins in `ALLOWED_ORIGINS`. Never use the example invite code or a checked-in secret in a deployment.
- Before handling real users, configure email ownership verification, password recovery, and authentication rate-limiting at the API gateway.

## Product prototype scope

- Public: welcoming landing page with student community photography, secure sign-in, and account creation with separate C1 participation, C2 research, and C3 leaderboard choices. The choices default off; C2/C3 require C1. Student photos are served locally and credited to [Pexels](https://www.pexels.com/).
- For a presentation, use **Preview student space**, **Preview counsellor workspace**, **Preview lecturer sessions**, or **Preview research dashboard** on the landing page. Preview sessions use synthetic/sample data, do not create accounts, and can be switched or exited from the workspace sidebar.
- Student: redesigned wellbeing dashboard, class PIN check-in across five descriptive domains, personal progression chart, communities, mood and screening check-ins, resources, counsellor booking, messaging, assistant, consent controls, and help.
- Screening results do not automatically contact a counsellor or send an alert. Students can access the always-visible Support & contacts page independently of their check-in responses.
- Lecturer preview: open one class session at a time with a six-digit PIN, close sessions, and see aggregate domain means only at a minimum of 10 distinct C2-consenting participants. A control can add 12 explicitly synthetic responses for presentation.
- Researcher preview: view session-level thresholded aggregates and a clear statement of which governance functions are not implemented. No participant-level export is available.
- Counsellor: overview, cases, risk monitoring, appointments, and messaging.
- Admin pages remain in the codebase but are not available through public account creation or sign-in. Lecturer and researcher access is preview-only and has no backend role or authorization.
- Student and counsellor registration, sign-in, session restore, account research-consent flag, and logout use the FastAPI backend. Longitudinal check-ins, class sessions, C1/C2/C3 consent history, aggregation, counselling workflows, appointments, messages, analytics, and research views are browser-local prototype features; they are not secured backend services. Never use these features for real health records, research collection, triage, or care decisions.
- Longitudinal prototype data are saved in browser local storage. Do not use real participant data: row-level security, production consent enforcement/audit, approved research extraction, retention and deletion automation, small-cell complementary suppression, offline support, and verified support escalation are not implemented.

### Hali Five-Area Check-In

The class check-in is a short reflection across Academic, Spiritual, Social, Physical, and Psychological wellbeing. Students consider the past 7 days and respond to one plain-language statement for each area using a five-point agreement scale. Spiritual wellbeing is framed inclusively around meaning, purpose, values, or inner grounding, with or without religion or faith.

This is a Hali-curated prompt set, not a validated questionnaire, clinical screening tool, or single overall wellbeing score. The five areas are shown separately to support self-awareness; responses should not be used for grading, diagnosis, or individual surveillance. A single item per area is only a starting point and needs Kenyan student input, cognitive testing, and ethical review before research or service use. The current prototype still stores responses in browser local storage and must only be demonstrated with sample data.
- Students and counsellors can open **My profile** from their workspace navigation to view their name, username, email, account type, and consent choices. Students also see their Hali pseudonym.
- The communities directory is a starter example, not an official university listing. Social buttons open public platform searches; they are not verified club accounts or social sign-in. Joining a group is saved only in the current browser and does not enroll or notify a real group. Replace the sample directory and links with university-verified details before launch.
- The project also includes a PWA manifest and build-generated service worker. It is registered only in production builds (`npm run build && npm run preview`).

## Structure

The frontend is organized into `components/`, `layouts/`, `pages/`, `services/`, `context/`, `hooks/`, `utils/`, and `data/`. The separately maintained backend repository contains the authentication API and creates its initial tables at startup.
