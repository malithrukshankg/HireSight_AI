# HireSight AI -- React Frontend Rules

This is the HireSight AI React frontend (Vite + TypeScript).

Use a **type-based (layer / horizontal)** project structure. Group files by kind, not by feature.

Always follow the root `CLAUDE.md` for system-wide architecture concerns (Auth0, roles, API gateway).

## 1. Directory Structure (Type-Based)

Under `front_end/src/`, use this layout:

```
src/
+-- components/
|   +-- ui/           # Generic reusable: Button, Card, Input, Modal
|   +-- layout/       # Header, Sidebar, Footer, PageLayout, RoleGuard, RoleRedirect
|   +-- forms/        # Shared form wrappers and field components
+-- pages/            # Route-level screens
|   +-- admin/        # AdminLayout, Dashboard, etc.
|   +-- recruiter/    # RecruiterLayout, Dashboard, etc.
|   +-- candidate/    # CandidateLayout, Dashboard, etc.
+-- hooks/            # Custom hooks (useAuth, useApi, useCurrentRole, etc.)
+-- services/         # API client, Auth0 wrapper, external calls
+-- store/            # Global state (Redux/Zustand) if used
+-- utils/            # Pure helpers, formatters, constants
+-- types/            # Shared TypeScript types/interfaces
+-- routes/           # Route config, lazy loading
+-- assets/
+-- App.tsx
+-- main.tsx
+-- index.css
```

- Do NOT introduce feature-based top-level folders (e.g. `features/auth/`) unless explicitly requested.
- New UI building blocks go in `components/ui/` or `components/layout/`.
- Route-level screens go in `pages/`; route definitions in `routes/`.

## 2. Components

- `components/ui/` -- Presentational, reusable, minimal props. No API calls or Auth0 inside.
- `components/layout/` -- Structure and shell (Header, Footer, RoleGuard, RoleRedirect). May use auth for conditional rendering.
- `components/forms/` -- Shared form components only; otherwise keep forms next to the page.
- One component per file. Name the file to match the component (e.g. `Button.tsx` for `Button`).

## 3. Pages and Routes

- `pages/` -- One file per main route. Pages compose components and call hooks/services; keep them thin.
- `routes/` -- Central route configuration. Use React Router. Prefer lazy-loaded pages for code splitting.
- Protected routes must check Auth0 and redirect unauthenticated users.

## 4. Role-Aware Routing

The app uses role-specific URL paths and layout-owned routing.

### URL Structure

- `/` -- Redirects via `RoleRedirect` to the user's role home
- `/role` -- ChooseRole (confirm or switch role)
- `/admin` -- Admin-only routes
- `/recruiter` -- Recruiter-only routes
- `/candidate` -- Candidate-only routes

### Layout-Owned Routing

- Layouts (`pages/admin/AdminLayout.tsx`, `pages/recruiter/RecruiterLayout.tsx`, `pages/candidate/CandidateLayout.tsx`) import and render their own pages.
- Each layout uses `<Routes>` and `<Route>` internally for that role's screens.
- Do NOT import role-specific dashboards or pages in `routes/index.tsx`; only import the layouts.
- `routes/index.tsx` defines: `RoleGuard` -> `Layout` (as index child). The layout handles the rest.

### Adding New Role-Specific Pages

- Add new pages inside the role folder (e.g. `pages/admin/Settings.tsx`).
- Add the route inside the layout's `<Routes>`.
- Do NOT add role-specific routes to `routes/index.tsx`.

### Shared vs Role-Specific Code

- Shared: `components/ui/`, `components/layout/`, `hooks/`, `services/`, `utils/`, `types/`
- Role-specific: `pages/admin/`, `pages/recruiter/`, `pages/candidate/`
- Shared components must remain role-agnostic; no role checks inside `components/ui/`.

### Role Guards

- Use `RoleGuard` with `allowedRoles` for `/admin`, `/recruiter`, `/candidate`.
- Use `RoleRedirect` for `/` to send users to `/{role}` or `/role`.
- Use `useCurrentRole()` from `hooks/useCurrentRole.ts` when the UI needs to branch on role.

## 5. Hooks

- `hooks/` -- Custom hooks only. Examples: `useAuth`, `useApi`, `useCurrentRole`, `useLocalStorage`.
- Hooks must not contain JSX.

## 6. Services

- `services/` -- All external I/O: API client (base URL, auth headers), Auth0 config wrapper.
- API calls must use the Auth0 access token via `getAccessTokenSilently`. Do not put raw fetch logic in components or pages.

## 7. State, Utils, Types

- `store/` -- Global state (Redux/Zustand) if used.
- `utils/` -- Pure functions, constants, formatters. No React or DOM-specific code.
- `types/` -- Shared TypeScript interfaces/types. Page/component-specific types can live next to the file.

## 8. File Safety and Scope

- Do NOT delete files or folders without explicit approval.
- Do NOT modify unless explicitly instructed:
  - `vite.config.ts`, `index.html`, root `package.json`
  - Auth0 provider setup in `main.tsx`
- Only change files required for the requested task. Minimal diffs only.
- Do not refactor or "improve" unrelated code.

## 9. UI Theme

Follow the established atmospheric warm theme:

- Accent color: Orange (`#f97316`, Tailwind: `bg-accent`, `text-accent`) for primary buttons, links, emphasis
- Backgrounds: `bg-atmospheric` gradient (warm amber -> slate blue). Cards/panels use `bg-white/10`, `border-white/20`, `backdrop-blur-sm`
- Text: `text-white` for headings, `text-white/90` or `text-white/80` for secondary
- Primary buttons: `bg-accent` with `hover:bg-accent-hover`, white text
- Secondary buttons: `border-2 border-white/50 bg-white/10` with `hover:bg-white/20`, white text
- Error states: `bg-red-500/20 text-red-100`
- Header/Footer: `bg-black/20 border-white/10` with white text and orange accents
- Theme tokens defined in `index.css`. Do not introduce conflicting palettes (violet, blue accents, etc.)

## 10. Auth0

- Authentication is Auth0 only. No password-based login.
- Use `@auth0/auth0-react`. Get access tokens via `getAccessTokenSilently` for API calls.
- Align with backend `auth0_sub` and role assumptions.

## 11. Refactors

- Describe the plan before refactoring (what moves where and why).
- If a change blurs the type-based structure or touches routing/auth, ask for confirmation when unsure.

## Priority

1. Keep the type-based structure (components, pages, hooks, services, utils, types, routes)
2. Follow role-aware routing (layouts own their pages; routes/index.tsx imports layouts only)
3. Keep auth and API access in services/hooks, not scattered in components
4. Make minimal, targeted changes
5. Use the atmospheric warm theme for all new UI
