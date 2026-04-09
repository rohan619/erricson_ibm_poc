#!/usr/bin/env bash
set -euo pipefail

require_var() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    echo "Missing required environment variable: $name" >&2
    return 1
  fi
}

require_cmd() {
  local name="$1"
  if ! command -v "$name" >/dev/null 2>&1; then
    echo "Required command not found: $name" >&2
    return 1
  fi
}

upload_result() {
  local status="$1"
  local failure_msg="${2:-}"
  cat > results.json <<JSON
{"resultStatus":"${status}","failureMessage":"${failure_msg}"}
JSON
  gcloud storage cp results.json "${CLOUD_DEPLOY_OUTPUT_GCS_PATH}/results.json" >/dev/null
}

on_error() {
  local line="$1"
  upload_result "FAILED" "GitOps update failed at line ${line}"
}

trap 'on_error $LINENO' ERR

require_var CLOUD_DEPLOY_OUTPUT_GCS_PATH
require_var CLOUD_DEPLOY_TARGET
require_cmd gcloud
require_cmd git
require_cmd sed

IMAGE_REPO="${CLOUD_DEPLOY_customTarget_IMAGE_REPO:-${IMAGE_REPO:-}}"
IMAGE_DIGEST="${CLOUD_DEPLOY_customTarget_IMAGE_DIGEST:-${IMAGE_DIGEST:-}}"
GITOPS_REPO="${CLOUD_DEPLOY_customTarget_GITOPS_REPO:-${GITOPS_REPO:-rohan619/erricson_ibm_app_repo}}"
GITOPS_BRANCH="${CLOUD_DEPLOY_customTarget_GITOPS_BRANCH:-${GITOPS_BRANCH:-main}}"
GITOPS_PAT_SECRET="${CLOUD_DEPLOY_customTarget_GITOPS_PAT_SECRET:-${GITOPS_PAT_SECRET:-}}"
GITOPS_PAT="${CLOUD_DEPLOY_customTarget_GITOPS_PAT:-${GITOPS_PAT:-}}"

require_var IMAGE_REPO
require_var IMAGE_DIGEST

if [[ -z "${GITOPS_PAT}" && -n "${GITOPS_PAT_SECRET}" ]]; then
  GITOPS_PAT="$(gcloud secrets versions access latest --secret="${GITOPS_PAT_SECRET}")"
fi

if [[ -z "${GITOPS_PAT}" ]]; then
  echo "Provide GITOPS_PAT (preferred) or GITOPS_PAT_SECRET for GitOps repo push auth" >&2
  exit 1
fi

case "${CLOUD_DEPLOY_TARGET}" in
  *qa*|*staging*)
    KUSTOMIZATION_FILE="overlays/staging/kustomization.yaml"
    ;;
  *prod*)
    KUSTOMIZATION_FILE="overlays/prod/kustomization.yaml"
    ;;
  *)
    echo "Unsupported target name: ${CLOUD_DEPLOY_TARGET}" >&2
    exit 1
    ;;
esac

workdir="$(mktemp -d)"
cleanup() {
  rm -rf "${workdir}"
}
trap cleanup EXIT

repo_url="https://x-access-token:${GITOPS_PAT}@github.com/${GITOPS_REPO}.git"
git clone --depth 1 --branch "${GITOPS_BRANCH}" "${repo_url}" "${workdir}/repo" >/dev/null 2>&1

file_path="${workdir}/repo/${KUSTOMIZATION_FILE}"
if [[ ! -f "${file_path}" ]]; then
  echo "Kustomization file not found: ${KUSTOMIZATION_FILE}" >&2
  exit 1
fi

if grep -qE '^[[:space:]]*newName:' "${file_path}"; then
  sed -i "s|^[[:space:]]*newName: .*|    newName: ${IMAGE_REPO}|g" "${file_path}"
fi

if grep -qE '^[[:space:]]*digest:' "${file_path}"; then
  sed -i "s|^[[:space:]]*digest: .*|    digest: ${IMAGE_DIGEST}|g" "${file_path}"
else
  cat >> "${file_path}" <<YAML

images:
  - name: my-app-image
    newName: ${IMAGE_REPO}
    digest: ${IMAGE_DIGEST}
YAML
fi

cd "${workdir}/repo"
git config user.name "Cloud Deploy GitOps Bot"
git config user.email "cloud-deploy-bot@users.noreply.github.com"
git add "${KUSTOMIZATION_FILE}"

if git diff --cached --quiet; then
  upload_result "SUCCEEDED" "No changes required"
  exit 0
fi

git commit -m "clouddeploy(${CLOUD_DEPLOY_TARGET}): update image digest to ${IMAGE_DIGEST}" >/dev/null
git push origin "${GITOPS_BRANCH}" >/dev/null 2>&1

upload_result "SUCCEEDED" ""
