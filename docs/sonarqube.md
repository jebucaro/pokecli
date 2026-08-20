# SonarQube Local Analysis

Run static analysis and coverage reporting against your SonarQube Community server from your local machine.

## Prerequisites

- A running SonarQube Community server accessible from your machine
- A project created on the server with key `pokecli`
- A project analysis token (generated in SonarQube > Your Project > Project Settings > Analysis Tokens)
- Python >= 3.12 and [uv](https://github.com/astral-sh/uv)

## One-Time Setup

1. Install project dependencies (includes `pysonar` and `pytest-cov`):

   ```bash
   uv sync
   ```

2. Create your local environment file:

   ```bash
   cp .env.sample .env
   ```

3. Edit `.env` and fill in your values:

   ```env
   SONAR_HOST_URL=http://your-sonar-server:9000
   SONAR_TOKEN=sqp_xxxxxxxxxxxxxxxxxxxx
   ```

## Usage

### Using Make (recommended)

```bash
# Full pipeline: run tests with coverage, then scan
make sonar

# Run only tests and generate coverage report
make coverage

# Run only the SonarQube scan (assumes coverage.xml already exists)
make sonar-only

# Clean up generated artifacts
make clean
```

### Using the shell script

```bash
# Full pipeline
./scripts/sonar.sh

# Scan only (skip tests, use existing coverage.xml)
./scripts/sonar.sh --scan
```

You can also run the script through uv:

```bash
uv run scripts/sonar.sh
```

## What Each Target Does

| Target / Command | Description |
|-----------------|-------------|
| `make coverage` | Runs `pytest --cov` and produces `coverage.xml` in Cobertura XML format |
| `make sonar` | Runs `make coverage` then invokes `pysonar` to submit results |
| `make sonar-only` | Invokes `pysonar` without re-running tests |
| `make clean` | Removes `coverage.xml`, `.coverage`, and `.scannerwork/` |

## Configuration

Non-sensitive SonarQube properties are stored in `pyproject.toml` under `[tool.sonar]`:

```toml
[tool.sonar]
projectKey = "pokecli"
projectName = "pokecli"
sources = "src"
tests = "tests"
python.coverage.reportPaths = "coverage.xml"
exclusions = "**/__pycache__/**,**/.venv/**"
sourceEncoding = "UTF-8"
```

Sensitive values (`SONAR_HOST_URL`, `SONAR_TOKEN`) are loaded from the `.env` file, which is gitignored.

## Troubleshooting

### Connection refused

```
ERROR: Unable to connect to SonarQube server
```

- Verify `SONAR_HOST_URL` in `.env` is correct and reachable (`curl $SONAR_HOST_URL/api/system/status`)
- Check that your firewall allows the connection

### Invalid token / 401 Unauthorized

```
ERROR: Not authorized. Analyzing this project requires authentication.
```

- Regenerate the token in SonarQube and update `SONAR_TOKEN` in `.env`
- Ensure the token has "Execute Analysis" permission for the project

### Missing coverage.xml

```
WARN: No coverage report found for sonar.python.coverage.reportPaths
```

- Run `make coverage` before `make sonar-only`, or just use `make sonar` which does both
- Verify tests pass: `uv run pytest`

### Project not found on server

```
ERROR: Project 'pokecli' not found
```

- Create the project on your SonarQube server first
- Ensure `projectKey` in `pyproject.toml` matches the key on the server

## How It Works

1. `pytest-cov` runs the test suite and generates a Cobertura XML coverage report (`coverage.xml`)
2. `pysonar` (the official SonarSource Python scanner) reads configuration from `[tool.sonar]` in `pyproject.toml`
3. The scanner picks up `SONAR_HOST_URL` and `SONAR_TOKEN` from environment variables (loaded from `.env`)
4. Source code and the coverage report are analyzed and submitted to your SonarQube server
5. Results are visible on your SonarQube dashboard at `$SONAR_HOST_URL/dashboard?id=pokecli`
