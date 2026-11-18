# Module 11 changes to existing files

| File | Change |
| --- | --- |
| `app/models/calculation.py` | Maps `a` and `b` to the first two entries in `inputs` with SQLAlchemy hybrid properties. Adds `from_create()` to pass validated operands and an explicit owner to the existing polymorphic factory. The JSON column preserves compatibility with existing rows and list-based calculations. |
| `app/schemas/calculation.py` | Accepts the assignment's operation names and binary operands, validates finite numbers, and reuses the zero-divisor check. Retains support for the legacy inputs list. Adds `CalculationRead`, which computes the result from an ORM instance. |
| `app/schemas/__init__.py` | Exports `CalculationRead` alongside the existing schemas. |
| `.github/workflows/test.yml` | Connects the test job to PostgreSQL 16, runs the full suite with Chromium and app coverage, and publishes the existing Docker tags to the configured Docker Hub account and repository after the existing image scan passes. |
| `tests/conftest.py` | Starts the existing browser-test server with the interpreter running pytest so it can import the same installed dependencies. |
| `tests/e2e/test_e2e.py` | Uses Playwright's retrying text assertions for both calculation responses, which render after an asynchronous request. |
| `requirements.txt` | Pins urllib3 to 2.8.0, the first release that fixes CVE-2026-97689. |
| `README.md` | Adds calculation usage, local test commands, repository links, and Docker Hub configuration. |
