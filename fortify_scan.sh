Accounts: Sign in with GitHub#!/usr/bin/env bash
set -euo pipefail

# Simple helper script to run Fortify SCA inside Docker if available.
# It expects either FORTIFY_SCA_IMAGE env var or fortify installed locally.

if [[ -n "${FORTIFY_SCA_IMAGE:-}" ]]; then
  echo "Running Fortify SCA using image $FORTIFY_SCA_IMAGE"
  docker run --rm -v "$PWD":/src -w /src "$FORTIFY_SCA_IMAGE" sourceanalyzer -b project -clean || true
  docker run --rm -v "$PWD":/src -w /src "$FORTIFY_SCA_IMAGE" sourceanalyzer -b project -scan -f results.fpr || true
else
  if command -v sourceanalyzer >/dev/null 2>&1; then
    echo "Running local Fortify sourceanalyzer"
    sourceanalyzer -b project -clean || true
    sourceanalyzer -b project -scan -f results.fpr || true
  else
    echo "Fortify SCA not found. Set FORTIFY_SCA_IMAGE or install Fortify and ensure 'sourceanalyzer' is on PATH."
    exit 0
  fi
fi
