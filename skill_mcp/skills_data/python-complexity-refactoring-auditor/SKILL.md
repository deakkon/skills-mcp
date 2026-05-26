---
name: python-complexity-refactoring-auditor
description: Use when auditing Python code complexity, measuring maintainability, finding refactoring hotspots, or creating CI gates for complexity.
license: Apache-2.0
metadata:
  author: community
  version: "1.0"
  tags: [python, complexity, refactoring, radon, ruff, xenon, cognitive-complexity, static-analysis, clean-code]
  platforms: [claude-code, cursor, windsurf, any]
  triggers:
    - audit Python code complexity
    - Python code complexity
    - refactoring hotspots Python
    - measure Python maintainability
    - Python complexity CI gates
    - radon cc
    - xenon
    - refactor complex Python code
---

# Python Complexity Refactoring Auditor

## Goal

Assess Python code complexity and produce a prioritized, behavior-preserving refactoring plan.

## Workflow

1. Inspect repository structure.
2. Run static checks:
   - `ruff check . --select C901,PLR0911,PLR0912,PLR0913,PLR0915`
   - `radon cc . -s -a`
   - `radon mi . -s`
   - `xenon --max-absolute B --max-modules A --max-average A .`
3. Identify hotspots:
   - High cyclomatic complexity
   - Too many branches
   - Too many statements
   - Too many arguments
   - Large modules
   - Raw dict domain models
   - Stringly typed business rules
   - Repeated scoring formulas
4. Classify each hotspot:
   - Algorithmic complexity
   - Cognitive complexity
   - Data-shape complexity
   - Architectural complexity
   - Testability complexity
5. Recommend refactoring patterns:
   - Strategy
   - Specification
   - Policy Object
   - Value Object
   - Domain Model
   - Functional Core, Imperative Shell
   - Bounded Context split
6. Before suggesting major refactors, recommend characterization or golden-master tests.
7. Output:
   - Executive summary
   - Ranked hotspots
   - Risk level
   - Recommended pattern
   - Suggested first PR
   - CI guardrails
