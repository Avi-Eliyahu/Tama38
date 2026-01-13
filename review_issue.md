# Code Review: Tama38 — Review Issue Template and Checklist

This file contains a summary of a high-level code review for the Avi-Eliyahu/Tama38 repository and an issue template/checklist to use when filing review items.

Repository observations
- Repository: Avi-Eliyahu/Tama38
- Description: TAMA38 Urban Renewal Management Platform
- Languages (by percent): Python (47.9%), TypeScript (35.4%), HTML (14.6%), JavaScript (0.8%), Shell (0.7%), PowerShell (0.3%)
- Notable files/directories observed (non-exhaustive):
  - backend/
    - backend/Dockerfile, docker-compose.yml
    - backend/pyproject.toml, requirements.txt, alembic migration folder
    - backend/app/api/v1/ (many large endpoint modules: reports.py (33KB), approvals.py (21KB), owners.py (25KB), projects.py, tasks.py, etc.)
    - backend/app/core/, backend/app/models/, backend/app/services/
    - backend/seed_database.py (seed script, ~20KB)
  - frontend/ (TypeScript + HTML UI)
  - Several large documentation files and binary docs in the repo root (Tama38_SRD.docx ~6MB, Tama38_SRD.md, TAMA38_Design_document.md, UI mockups .html files)

High-level strengths
- Clear domain focus (urban renewal / TAMA38) with substantial design and documentation present.
- Backend organized with a FastAPI-like structure (app/api, core, models, services) and database migration support (alembic).
- Docker and docker-compose present for local/dev environment.

Primary concerns and recommended actions
1) Large monolithic API modules
   - Evidence: multiple large Python files under `backend/app/api/v1` (e.g., `reports.py`, `approvals.py`, `owners.py`, `projects.py`, `tasks.py`).
   - Risk: Reduced maintainability, harder to test, higher chance of merge conflicts.
   - Recommendation: Refactor into smaller routers/controllers by resource or subrouters. Move business logic into services and keep endpoints thin.

2) Lack of automated tests and CI (not observed)
   - Recommendation: Add unit and integration tests for core services and API endpoints. Add CI (GitHub Actions) to run tests, linters, and type checks on PRs.

3) Typing and static analysis
   - Recommendation: Add type hints across Python code, enable mypy, and adopt linters (ruff/flake8) plus formatting (black/isort). Add pre-commit hooks.

4) Dependency management
   - Observation: `requirements.txt` and `pyproject.toml` both present.
   - Recommendation: Standardize on one dependency manager (poetry or pinned requirements). Pin versions for production builds. Add dependency scanning (Dependabot or similar).

5) Large binaries and docs in the repo
   - Evidence: `Tama38_SRD.docx` (~6MB) and other binary `.docx` files.
   - Recommendation: Move large binaries to releases or external storage (or use Git LFS) and keep lightweight Markdown in the repo.

6) Documentation & contributor experience
   - Recommendation: Add `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and PR/issue templates. Ensure README/QUICK_START contain clear local run & test instructions.

7) Security and secret management
   - Recommendation: Audit for secrets. Ensure config values (DB passwords, JWT secrets) are injected via environment variables and not checked in. Enable secret scanning.

8) Database and migrations
   - Recommendation: Keep alembic migrations under source control (they appear present). Add migration checks in CI and document upgrade/deploy steps.

9) Frontend toolchain and quality checks
   - Recommendation: Add ESLint, stricter TypeScript settings, and frontend unit tests. Add a frontend build check to CI.

10) Test data and seed scripts
   - Observation: `backend/seed_database.py` is large.
   - Recommendation: Keep seed data minimal; use fixtures for tests. Avoid seeding large datasets in CI.

Suggested immediate issues to open
- Split monolithic API modules into smaller routers and move business logic into services.
- Add baseline CI: run tests, linters, and type checks.
- Add pre-commit configuration (black, ruff, isort).
- Remove or relocate large binary docs from the repository.
- Add CONTRIBUTING.md, PR/Issue templates, and CODE_OF_CONDUCT.md.
- Standardize and pin dependencies; add dependency scanning.

Review issue template (use when filing a code-review issue)
---
Title: [CODE-REVIEW] <short description of the issue or area>

Repository: Avi-Eliyahu/Tama38  
Area: (backend | frontend | docs | infra | tests | security | other)  
Severity: (critical | high | medium | low)  
Labels: code-review, <area>, <severity>

Description:
A concise description of the problem or code smell.

Files / Locations:
- path/to/file.py:lineno (if relevant)
- backend/app/api/v1/reports.py
- backend/app/api/v1/approvals.py

Observed behaviour:
What the code currently does and why it is problematic.

Expected behaviour:
What we expect the code to do after the change.

Suggested fix or recommendation:
- Short, actionable steps to resolve the issue (include code examples or references to patterns used elsewhere in the repo).

Acceptance criteria / Tests:
- List tests or checks that must pass to consider the issue resolved.

Notes / Related resources:
- Design docs: TAMA38_Design_document.md
- Quick start: QUICK_START.md

Checklist for reviewers (use as a template when publishing review issues)
- [ ] Reproduced locally where applicable
- [ ] Added unit tests covering the change
- [ ] Added / updated integration or e2e tests if applicable
- [ ] Added changelog entry if behavior changed
- [ ] Ensured no secrets are present in the diffs
- [ ] Followed repository style (formatting/linting)
- [ ] Updated documentation where necessary

How I assessed the repository in this pass
- I inspected repository structure and file sizes for backend/app and doc files, checked for infra files (Dockerfile, docker-compose.yml, alembic) and looked for evidence of tests and CI. This is a high-level review; a deeper review requires running the code and reading modules in detail.

--- 