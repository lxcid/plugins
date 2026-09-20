---
id: test-design
version: 1
section: Test Design
---

## Test Design

- **TDD for behavior changes.** Smallest meaningful failing test first; tests are part of the design.
- **Test at the lowest useful level** with the real contract for that surface: state transitions for domain logic, request/response for HTTP handlers, auth boundaries for identity, user-visible state changes for UI. Cover unhappy paths (authorization failures, stale versions, malformed input, expiry, retries, idempotency, boundaries).
- **Avoid over-stubbing.** A test that passes while real integration fails is worse than no test. When a unit test needs heavy mocking, prefer a narrower pure-helper test, a handler-level test with real local collaborators, or a smoke check.
- **Skipping tests is an explicit engineering call** — justify it with the reason, what verification you ran instead, and what test to add if the surface grows.
