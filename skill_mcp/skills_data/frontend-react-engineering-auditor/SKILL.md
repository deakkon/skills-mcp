---
name: frontend-react-engineering-auditor
description: Use when reviewing, refactoring, debugging, or improving a React or TypeScript frontend codebase. Focus on component architecture, state management, accessibility, performance, testability, and safe implementation plans.
license: Apache-2.0
metadata:
  author: community
  version: "1.0"
  tags: [react, typescript, frontend, component-architecture, state-management, accessibility, a11y, performance, testing, clean-code]
  platforms: [claude-code, cursor, windsurf, any]
  triggers:
    - review React codebase
    - reduce frontend complexity
    - refactor React component
    - audit frontend architecture
    - improve React performance
    - improve accessibility React
    - improve test coverage React
    - review frontend PR
    - frontend implementation plan
---

# Frontend React Engineering Auditor

## Purpose

Help review and improve React or TypeScript frontend codebases with practical, modern frontend engineering standards.

Use this skill for requests like:

* Review this React codebase
* Reduce frontend complexity
* Refactor this component
* Audit frontend architecture
* Improve React performance
* Improve accessibility
* Improve test coverage
* Review a frontend PR
* Create a frontend implementation plan

## Operating principles

Prefer simple, explicit, boring React code.

Optimize for:

1. Correctness
2. Readability
3. Accessibility
4. Testability
5. Performance where it matters
6. Design-system consistency
7. Small, reviewable changes

Do not introduce abstraction, global state, memoization, or new dependencies unless there is a clear benefit.

## First steps

Before changing code:

1. Inspect project structure and `package.json`.
2. Identify the framework: React, Next.js, Remix, Vite, React Native, or other.
3. Identify tooling: TypeScript, linting, formatting, tests, styling, and component library.
4. Read project guidance such as `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `tsconfig.json`, and lint or test configs.
5. Run existing checks when possible: lint, typecheck, test, and build.

## What to review

### Component complexity

Flag components that are too large, mix too many responsibilities, duplicate UI logic, accept too many props, contain deep conditional rendering, or combine data fetching with presentation.

Prefer small components, clear props, extracted hooks for reusable behavior, pure helpers for formatting, and explicit loading, empty, error, and success states.

### State management

Prefer the simplest valid state owner:

1. Local state
2. Derived state
3. URL/search params
4. Context
5. Server-state cache
6. External global store

Flag duplicated derived state, unnecessary global state, broad contexts, loose boolean state machines, and effects used only to synchronize state that could be computed.

### Effects and data fetching

Review `useEffect` carefully.

Flag effects that derive state, hide event logic, combine unrelated work, miss cleanup, have unsafe dependencies, or fetch data without stale-response handling.

Prefer framework data APIs, typed API clients, stable query keys, clear error states, and API adapter layers when backend shapes should not leak into UI.

### TypeScript

Flag `any`, unsafe casts, overly broad types, duplicated API shapes, optional fields used without guards, and impossible states represented by loose booleans.

Prefer explicit prop types, discriminated unions for UI states, typed API boundaries, and narrow helper functions.

Example:

```ts
type LoadState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "error"; error: Error }
  | { status: "success"; data: T };
```

### Accessibility

Check semantic HTML, keyboard navigation, focus states, form labels, accessible names, error messaging, dialogs, color contrast, and reduced-motion behavior.

Flag clickable `div`s, icon-only buttons without labels, hover-only interactions, inaccessible custom controls, and modals without focus management.

### Performance

Do not optimize blindly. First identify real bottlenecks.

Flag unnecessary re-renders, unstable props, large lists without virtualization, oversized bundles, repeated network calls, expensive derived calculations, and context values that change too often.

Use memoization only when it solves a measured or obvious problem.

### Testing

Prefer behavior-focused tests using accessible queries and realistic user interactions.

Prioritize tests for critical flows, complex conditional rendering, forms, data-fetching states, permissions, accessibility basics, and regression bugs.

## Complexity tripwires

Flag code when it has:

* Component over 200 lines
* Function over 50 lines
* More than 7 props
* More than 3 levels of conditional rendering
* More than 3 nested ternaries
* Many `useEffect` blocks in one component
* Heavy use of `any`
* Repeated API mapping or validation logic
* Multiple booleans representing one UI state
* Broad context providers causing many re-renders

These are review triggers, not automatic failures.

## Recommended refactoring patterns

Use these patterns when they reduce complexity:

* Presentational/container split
* Custom hook extraction
* Adapter layer for API data
* Discriminated union or state machine for complex UI state
* Compound components for structured component APIs
* Design-system primitives for repeated UI patterns
* Feature folders for product-area boundaries

Prefer feature-oriented structure when helpful:

```text
features/
  billing/
    components/
    hooks/
    api/
    types/
    tests/
```

## Output format

When reviewing code, produce:

1. Summary
2. Top risks
3. Component complexity hotspots
4. State and data-flow issues
5. Accessibility issues
6. Performance issues
7. Testing gaps
8. Recommended refactoring plan
9. First safe PR

For each finding, include file path, issue, impact, recommended fix, risk level, and whether it should block merge.

## Implementation rules

When editing code:

* Make the smallest safe change
* Preserve behavior unless asked otherwise
* Avoid unrelated rewrites
* Avoid new dependencies unless justified
* Keep public component APIs stable unless migration is included
* Update tests when behavior changes
* Run available checks
* Report what was and was not verified

## Severity

* Critical: production breakage, security issue, data loss, or inaccessible core flow
* High: likely user-visible bug or broken important flow
* Medium: maintainability, testability, performance, or accessibility risk
* Low: naming, style, or local cleanup
