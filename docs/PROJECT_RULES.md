# Project rules

**Author:** Vasiliy Zdanovskiy  
**email:** vasilyvz@gmail.com  

This document defines the rules for developing and maintaining the Stellar Seismic Catalog project.

---

## 1. Language and documentation

- **User communication:** Russian.
- **Documentation (in repo):** English only, unless the product owner explicitly requests another language.
- **Code, comments, docstrings, tests:** English only.
- **Locale/symbols:** Ukraine (no Russian state symbols; Russian is used only as the language of communication).

---

## 2. Code quality and style

- **Formatting:** Black. Run after each edit; fix all reported issues.
- **Linting:** Flake8. No unresolved issues before moving on.
- **Types:** Mypy. Fix all reported type errors.
- **Imports:** All at the top of the file, except when implementing explicit lazy loading.
- **No edits outside the project** without explicit user permission (especially no changes to system or external code).

---

## 3. File and class size

- **Max file size:** 350–400 lines for code files (excluding data and docs).
- **One class per file** as a default; exceptions: small enums, exception classes.
- **Large classes:** Split into a facade and smaller modules; do not leave oversized files “for later”.

---

## 4. Docstrings and declarations

- **Every code file** must have a module-level docstring with at least: Author (Vasiliy Zdanovskiy), email (vasilyvz@gmail.com).
- **Classes and public methods** must have docstrings (and comments in English where needed).
- **Production code:** No `pass` instead of implementation (except for abstract methods, which use `NotImplemented`). No hardcoded placeholders or “TODO” instead of real logic in production paths.
- **Declarative vs production:** Declarative code has full docstrings and signatures; production code is the same but with full implementations and no stray `pass`/hardcode.

---

## 5. Version control and tooling

- **Commit:** After each logical change or after a batch of related file changes; do not commit half-done work.
- **Push:** Only on explicit user request.
- **Environment:** Always use the project’s virtual environment (e.g. `.venv`). Do not use `--break-system-packages` for installs; activate the venv first.
- **Project id:** The project identifier for internal tools is stored in the `projectid` file in the repository root; use it in scripts and tooling as required.

---

## 6. Indexing and discovery

- After each batch of file changes, run the project’s **code_mapper** (or equivalent) so that indices in `code_analysis/` stay up to date (file/method index, descriptions, errors).
- Before adding new functionality, run **code_mapper** and check **code_analysis** indices to avoid duplicating existing behaviour.

---

## 7. Logging importance (0–10)

- Log messages carry an **importance** value 0–10 (business/operational impact and urgency).
- Follow the project’s importance scale (see the dedicated rules document): 0–2 diagnostics, 3–5 informational/notice, 6–7 warnings, 8 error, 9 severe, 10 critical.
- Importance is independent of log level (DEBUG/INFO/WARNING/ERROR/CRITICAL); set it according to impact.

---

## 8. Where to write

- **In repo (e.g. `docs/`):** Project documentation, plans, steps, structured bug reports.
- **In chat only:** Analyses, explanations, one-off Q&A, runbooks that are answers to a question rather than lasting project docs.
- **User override:** If the user explicitly says “put this in `docs/foo.md`” or “don’t create a file, answer in chat”, follow that.

---

## 9. Technical scope (from tech spec)

- **Stack:** Python 3; allowed libraries include numpy, pandas, astroquery, astropy, matplotlib.
- **Scripts:** At least `download_catalogs.py` (download) and `process_catalogs.py` (process and clean); placement per `docs/LAYOUT_STANDARDS.md` (e.g. `scripts/` or entry points from the package).
- **Outputs:** `stars_raw.csv`, `stars_clean.csv`, plots (e.g. PNG), and optionally `stellar_seismic_catalog.zip` as specified in the tech spec; paths per layout standards (e.g. `output/`, `plots/`).

These rules apply to all contributions and automated edits to the project.
