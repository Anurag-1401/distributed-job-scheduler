# Distributed Job Scheduler — Frontend

Minimal, professional React dashboard for the Distributed Job Scheduler internship project.

## Stack
- React 19 + Vite
- JSX
- Traditional CSS
- Axios
- React Router
- Recharts
- Vitest + React Testing Library

## Run locally

```bash
npm install
npm run dev
```

Set the API host in `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

The frontend expects the API routes documented in `docs-frontend-api-contract.md`.

## Production build

```bash
npm run build
npm run preview
```

## Tests

```bash
npm test
```

## Main features
- Authentication and protected routing
- Organizations and projects
- Queue configuration, pause/resume, priority, concurrency and retry policy
- Immediate, delayed, scheduled, cron and batch job creation
- Job explorer with pagination, filters and sorting
- Job lifecycle timeline and execution history
- Structured execution logs
- Worker health, heartbeat and utilization monitoring
- Dead Letter Queue inspection and retry
- Dashboard metrics, system health and recent jobs
- Polling without overlapping requests
- Toast notifications and confirmation dialogs
- Responsive traditional CSS
