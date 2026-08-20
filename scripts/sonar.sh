#!/usr/bin/env bash
# pokecli – Run SonarQube analysis locally
#
# Usage:
#   ./scripts/sonar.sh          Full pipeline (tests + coverage + scan)
#   ./scripts/sonar.sh --scan   Scan only (assumes coverage.xml exists)
#
# This script can also be invoked via: uv run scripts/sonar.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Load environment variables
if [ -f .env ]; then
    set -a
    # shellcheck source=/dev/null
    source .env
    set +a
else
    echo "ERROR: .env file not found. Copy .env.sample to .env and fill in your values." >&2
    exit 1
fi

# Validate required variables
if [ -z "${SONAR_HOST_URL:-}" ]; then
    echo "ERROR: SONAR_HOST_URL is not set in .env" >&2
    exit 1
fi

if [ -z "${SONAR_TOKEN:-}" ]; then
    echo "ERROR: SONAR_TOKEN is not set in .env" >&2
    exit 1
fi

# Parse arguments
SCAN_ONLY=false
if [ "${1:-}" = "--scan" ] || [ "${1:-}" = "--scan-only" ]; then
    SCAN_ONLY=true
fi

# Run tests with coverage (unless --scan flag is passed)
if [ "$SCAN_ONLY" = false ]; then
    echo "==> Running tests with coverage..."
    uv run pytest --cov=src/pokecli --cov-report=xml:coverage.xml --cov-report=term-missing
    echo ""
fi

# Run SonarQube scanner
echo "==> Running SonarQube analysis..."
uv run pysonar

echo ""
echo "==> Done. Check results at: ${SONAR_HOST_URL}/dashboard?id=pokecli"
