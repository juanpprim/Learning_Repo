# Frontend Basics with React

## Objectives
- Understand components, props, and state as React's core model.
- Fetch data from a backend API and render it (loading/error/success states).
- Handle forms and user input, and lift state up between components.

## Key concepts

> **Deep dive:** open [`key_concepts.html`](key_concepts.html) in a browser for animated explanations of each concept below.
- Function components + hooks (`useState`, `useEffect`) — the modern React model.
- Props (parent -> child data flow) vs. state (component-owned, triggers re-render).
- Controlled inputs for forms.
- `fetch`/`axios` for API calls, and handling loading/error states explicitly.
- Component composition vs. prop drilling (when you'd reach for context/a state library).

## Resources
- React docs — Quick Start: https://react.dev/learn
- React docs — "Synchronizing with Effects" (useEffect): https://react.dev/learn/synchronizing-with-effects
- Vite docs (fast dev server/build tool): https://vitejs.dev/guide/

## Checklist
- [ ] Scaffold a React app with Vite (`npm create vite@latest`).
- [ ] Build a component that fetches a list from an API and renders it, with
      loading and error states.
- [ ] Build a form component with controlled inputs that POSTs to the API on submit.
- [ ] Split state sensibly across 2-3 components (lift state up where needed).
- [ ] Style it minimally (plain CSS or a lightweight utility like Tailwind) so
      it's pleasant to look at.

## Mini-project
Build a UI for the `backend-api-fastapi/` CRUD API: list items, add a new
item via a form, mark items done, with proper loading/error handling — this
becomes the frontend half of `full-stack-capstone-project/`.
