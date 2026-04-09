#!/usr/bin/env bash
set -euo pipefail

fail_and_upload() {
  local message="$1"
  printf '{"resultStatus":"FAILED","failureMessage":"%s"}\n' "$message" > results.json
  gcloud storage cp results.json "${CLOUD_DEPLOY_OUTPUT_GCS_PATH}/results.json"
  exit 1
}

if [[ -z "${CLOUD_DEPLOY_OUTPUT_GCS_PATH:-}" ]]; then
  echo "Missing CLOUD_DEPLOY_OUTPUT_GCS_PATH" >&2
  exit 1
fi

IMAGE_REPO="${CLOUD_DEPLOY_customTarget_IMAGE_REPO:-${IMAGE_REPO:-}}"
IMAGE_DIGEST="${CLOUD_DEPLOY_customTarget_IMAGE_DIGEST:-${IMAGE_DIGEST:-}}"

if [[ -z "${IMAGE_REPO}" || -z "${IMAGE_DIGEST}" ]]; then
  fail_and_upload "Missing IMAGE_REPO or IMAGE_DIGEST deploy parameters"
fi

{
  echo "release: ${CLOUD_DEPLOY_RELEASE:-unknown}"
  echo "target: ${CLOUD_DEPLOY_TARGET:-unknown}"
  echo "image: ${IMAGE_REPO}@${IMAGE_DIGEST}"
} > rendered-manifest.yaml

gcloud storage cp rendered-manifest.yaml "${CLOUD_DEPLOY_OUTPUT_GCS_PATH}/rendered-manifest.yaml"
printf '{"resultStatus":"SUCCEEDED","manifestFile":"%s/rendered-manifest.yaml"}\n' "${CLOUD_DEPLOY_OUTPUT_GCS_PATH}" > results.json
gcloud storage cp results.json "${CLOUD_DEPLOY_OUTPUT_GCS_PATH}/results.json"
