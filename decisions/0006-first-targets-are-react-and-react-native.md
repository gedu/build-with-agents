---
id: decisions/0006-first-targets-are-react-and-react-native
type: decision
targets: [any]
status: validated
verified: 2026-08-04
sources: ["journal/2026-08-04-repo-skeleton-design.md"]
---

# 0006 — First target techs are React and React Native

## Context

Starting with five techs at once dilutes. Order matters more than it looks: starting with Go
or Python — where Eduardo has little experience — makes it impossible to tell *"the repo is
badly designed"* from *"I don't understand the tech"*.

So validate the structure with techs he already commands, then use Go or Python as the first
real learn-from-zero case, which is where the repo proves its actual value.

## Decision

React and React Native are the only targets in scope now; validate the structure with known
techs first.

## Consequences

| Consequence | Detail |
|---|---|
| Later order | Node, Python, Go, then Android/Kotlin + Kotlin Multiplatform, then iOS/Swift. |
| No empty target directories | A target directory is created when there is validated content for it. |
| Structural problems are attributable | A failure in a known tech is a repo-design failure, not a knowledge gap. |
| "backend" is a domain, not a tech | It overlaps the Node/Python/Go already listed, so it belongs in `theory/backend/` plus a concrete target — never as a `blocks/` directory. |
| Kotlin Multiplatform is one target | It covers Android and iOS, not two targets. |

## Alternatives

| Rejected | Reason |
|---|---|
| Start with five techs at once | Dilutes. |
| Start with Go or Python | Impossible to separate "badly designed repo" from "I don't understand the tech". |
| A `blocks/backend/` directory | "backend" is a domain, not a tech, and overlaps Node/Python/Go. |
| Android and iOS as two Kotlin Multiplatform targets | KMP is one target covering both. |
