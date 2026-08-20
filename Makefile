# pokecli – SonarQube local analysis
#
# Usage:
#   make coverage    Run tests and generate coverage.xml
#   make sonar       Run tests + coverage, then submit to SonarQube
#   make sonar-only  Submit to SonarQube (assumes coverage.xml exists)
#   make clean       Remove generated analysis artifacts
#
# Prerequisites:
#   1. Copy .env.sample to .env and fill in SONAR_HOST_URL and SONAR_TOKEN
#   2. Run `uv sync` to install dependencies

.PHONY: coverage sonar sonar-only clean

# Load .env if it exists
ifneq (,$(wildcard .env))
  include .env
  export
endif

coverage:
	uv run pytest --cov=src/pokecli --cov-report=xml:coverage.xml --cov-report=term-missing

sonar: coverage
	uv run pysonar

sonar-only:
	uv run pysonar

clean:
	rm -f coverage.xml .coverage
	rm -rf .scannerwork/
