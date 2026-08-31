# Release & Dependency Management

## semantic-release

Releases are fully automated via the `Release` GitHub Actions workflow
(`.github/workflows/release.yml`) on push to `main` and on `workflow_dispatch`.

- Tool: `python-semantic-release` (config in `pyproject.toml` `[tool.semantic_release]`).
- Version sources: `cron_scanner/__init__.py:__version__` and `setup.py:version`.
- Tag format: `v{version}`; `allow_zero_version = false`.
- The workflow builds sdist + wheel, runs `semantic-release version --push --vcs-release`,
  and force-moves a `latest` tag to the newest version tag.
- Commits are SSH-signed using the `SSH_SIGNING_KEY` secret.

### Commit message convention (required for releases)

Use **Conventional Commits** so semantic-release can derive versions and changelog
sections:

- `feat: ...` / `feat(scope): ...` → minor release
- `fix: ...` → patch release
- `feat!:` / `BREAKING CHANGE:` → major release
- `chore:`, `docs:`, `refactor:`, `test:`, `ci:`, `build:`, `perf:`, `style:`,
  `revert:` → no release (chore/chore(deps) appear under "Chores")
- `deps(scope): ...` is used by Dependabot (see below).

Do **not** manually edit `__version__` in `cron_scanner/__init__.py` or `version` in
`setup.py` — semantic-release manages both.

## Dependabot

`.github/dependabot.yml` configures two ecosystems:

- **pip** (weekly, `lockfile-only`): groups production minor/patch updates together;
  commit prefix `deps` with scope.
- **github-actions** (weekly): groups all action updates; up to 5 open PRs.

Dependabot PR titles follow `deps(scope): ...` and land in the "Chores" changelog
section on the next release.
