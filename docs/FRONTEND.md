# Frontend Architecture

This is the Next.js 14 frontend for the AI-Powered Dynamic Pricing Engine.

## Stack
- **Framework:** Next.js 14 (App Router)
- **Styling:** Tailwind CSS + shadcn/ui
- **State/Caching:** TanStack Query (React Query)
- **API Client:** Axios
- **Real-Time:** Socket.io-client
- **Testing:** Vitest + React Testing Library

## Directory Structure
- `src/app`: Next.js App Router pages and layouts.
- `src/components/layout`: Sidebar and Header components.
- `src/components/ui`: shadcn/ui primitive components.
- `src/hooks`: Custom hooks (e.g., `useSocket`).
- `src/lib`: Utilities and API clients.
- `src/providers`: React Context providers for Auth and TanStack Query.

## Authentication
JWT tokens are securely managed by the `AuthProvider`, attaching the Bearer token to all Axios requests automatically. The `middleware.ts` guards the `/(dashboard)` route.
