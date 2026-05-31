# AGENTS.md

Instructions for coding agents working in this repository.

## Project Overview

- This project is `oxl-ansible-webui`, an unofficial community WebUI for running and managing Ansible jobs locally.
- Backend code lives in `src/oxl_ansible_webui/`. The Django app is `src/oxl_ansible_webui/aw/`.
- Main backend areas are `aw/api_endpoints/` for DRF APIs, `aw/model/` for Django models, `aw/execute/` for job execution, `aw/config/` for runtime configuration, `aw/views/` for server-rendered pages, and `aw/auth.py` for custom authentication backends and middleware.
- Frontend code lives in `frontend/src/` and uses Svelte 5, TypeScript, Vite, TailwindCSS, and Flowbite/Flowbite-Svelte.
- Integration tests and sample Ansible content live under `test/`. Helper scripts live under `scripts/`.
- Documentation lives under `docs/source/` and contribution notes are in `CONTRIBUTE.md`.

## Environment

- The project venv lives at `.venv/` (managed by `uv`, Python 3.12). Set the IDE interpreter to `.venv/bin/python3`.
- Use a Python virtual environment for local development. `scripts/install_dev.sh` exits if it detects the system Python at `/usr/bin/python3`.
- The package metadata declares Python `>=3.11,<3.13`; most CI jobs use Python 3.12.
- Frontend CI uses Node.js 24.x. Run npm commands from `frontend/` unless a repository script handles the directory change.
- Runtime dependencies are in `requirements.txt`; lint, backend-test, and frontend-test extras are in `requirements_lint.txt`, `requirements_test_backend.txt`, and `requirements_test_frontend.txt`.
- Development and integration scripts create temporary SQLite DBs and may start or kill `oxl_ansible_webui` processes.

## Common Commands

- Install dev dependencies: `make install`
- Run containerized dev stack: `make run-dev`
- Run local dev app with initialization: `make run-dev-local-init`
- Run local dev app after initialization: `make run-dev-local`
- Build frontend once: `make build-fe-local` or `bash scripts/frontend/build.sh`
- Auto-build frontend during development: `make build-fe-local-auto`
- Lint Python and YAML: `make lint`
- Run full test script: `make test`
- Run backend unit tests: `make test-unit` or `python3 -m pytest`
- Run targeted integration tests: `make test-api`, `make test-job-exec`, `make test-webui`, `make test-auth`, `make test-db`
- Test Python package build/install behavior: `bash scripts/run_pip_build.sh`
- Frontend build/check: `cd frontend && npm run build`, `cd frontend && npm run check`

## Backend Guidelines

- Keep changes simple; the project explicitly values a simple WebUI.
- Treat this as API-first. New behavior should have clean external API semantics and follow existing DRF and `drf_spectacular` patterns in `aw/api_endpoints/`.
- Follow existing Python style: snake_case functions and variables, PascalCase classes, imports from `aw.*`, and the `.pylintrc` configuration.
- Pytest discovers files matching `*_pytest.py` as configured in `pytest.ini`. Auth-specific unit tests live in `aw/auth_pytest.py`.
- Do not commit generated Django migrations. Versioned release migrations under `src/oxl_ansible_webui/aw/migrations/` are tracked intentionally; normal development migrations are ignored.
- For MySQL/MariaDB-sensitive write paths, follow the project docs and call `close_old_mysql_connections()` from `aw.utils.db_handler` before DB writes when appropriate.
- Keep security in mind. Do not expose saved job credentials, API keys, `AW_SECRET`, database passwords, or SAML config. Preserve XSS validation and audit logging patterns for create/update/delete/execute actions.
- The app supports three auth modes controlled by `AW_AUTH`: `local` (default, password login), `header` (reverse-proxy supplies username via HTTP header, e.g. HAProxy sets `Remote-User`; configured via `AW_REMOTE_USER_HEADER`, default `HTTP_REMOTE_USER`), and `saml`. In `header` mode `ModelBackend` is disabled, local login is blocked, and the frontend hides logout/password-change UI. The header value must match an existing Django user — unknown users are never created automatically.
- Important fixes and features should update `CHANGELOG.md` when user-facing or release-relevant.

## Frontend Guidelines

- Svelte files use Svelte 5 runes such as `$state`, `$derived`, `$props`, and `$bindable`; follow nearby component patterns.
- Use existing API helpers in `frontend/src/util/api.ts` and shared state/types in `frontend/src/base/` before adding new fetch or state plumbing.
- Preserve the existing Tailwind/Flowbite visual language and dark-mode behavior.
- Vite has multiple entry points in `frontend/vite.config.ts`: `main`, `home`, `login`, `system`, and `login_saml`.
- If adding another Svelte app entry point, update `frontend/vite.config.ts` and `scripts/frontend/validate_prod_build.sh`.
- Frontend bundles are generated into `src/oxl_ansible_webui/aw/static_dev/dist` for development. Do not commit generated `frontend/dist/`, `static_dev/`, or `static_prod/dist/` output.
- Do not copy development bundles into `src/oxl_ansible_webui/aw/static/`; production static files are handled during release.

## Translations And Docs

- User-facing UI text should use the translation system rather than hard-coded strings.
- Translation files are under `src/oxl_ansible_webui/aw/config/languages/` and are loaded through `aw/config/language.py`.
- If adding new translation keys, add them for all existing languages or leave explicit follow-up notes where a translation is intentionally missing.
- Update `docs/source/` for behavior, configuration, security, or development workflow changes.

## Testing Notes

- Prefer targeted tests for the area changed before running the full suite.
- `make lint` runs PyLint with `pylint_django` and then `yamllint .`; YAML line length is configured to 160.
- `make test` builds the frontend, runs pytest, then API, job-execution, WebUI, SAML auth, CLI, and initialization checks.
- Integration scripts source `scripts/test_base.sh`, start the web app, use `/tmp` databases by default, and call `pkill -f oxl_ansible_webui` during cleanup.
- WebUI tests can capture screenshots when run with `AW_DEBUG=1`.

## Repository Hygiene

- Respect `.gitignore`; generated DB files, coverage files, frontend build output, and static build output should stay uncommitted.
- Avoid changing Docker, CI, or release scripts unless the task requires it; they encode project-specific workflow assumptions.
- Before touching security-sensitive code, inspect the nearby tests and docs in `docs/source/admin/security.rst`.
