# Ericsson IBM POC

End-to-end DevSecOps proof of concept for a Python web app deployed through a secure GitOps workflow.

This repository demonstrates:
- A small Flask application with health and telemetry endpoints
- CI testing and static analysis (pytest + SonarCloud + Fortify SCA)
- Container build via Google Cloud Build
- Binary Authorization attestation signing
- Automatic image digest update in a separate GitOps repo

## What This Project Does

On every push to `main`, GitHub Actions runs a pipeline that:

1. Executes application tests
2. Runs SonarCloud analysis
3. Runs Fortify SCA scan
4. Builds and pushes a container image to Artifact Registry
5. Resolves and exports the immutable image digest
6. Signs and creates a Binary Authorization attestation
7. Updates a second GitOps repository with the new image digest

This creates a secure delivery chain:

`Code -> Test -> Scan -> Build -> Sign -> GitOps Update -> Deployment`

## Tech Stack

- Python 3.10/3.11
- Flask
- Gunicorn
- psutil
- pytest
- GitHub Actions (self-hosted runner: `my-gke-runners`)
- SonarCloud
- Fortify SCA
- Google Cloud Build + Artifact Registry
- Google Binary Authorization
- GitOps repository update (Kustomize `newTag`)

## Repository Structure

```text
.
├── app.py                           # Flask app and routes
├── templates/index.html             # Dashboard UI
├── tests/test_app.py                # Unit tests
├── Dockerfile                       # Container build/runtime
├── fortify_scan.sh                  # Fortify scan helper
├── sonar-project.properties         # SonarCloud settings
├── requirements.txt                 # Python dependencies
└── .github/workflows/main.yml       # CI/CD pipeline
```

## Application Endpoints

- `GET /`  
  Renders dashboard with pod/system details and live CPU/memory usage bars.

- `GET /api/metrics`  
  Returns JSON with live CPU and memory utilization.
  Example response:
  ```json
  {
    "cpu": 22.3,
    "memory": 41.8
  }
  ```

- `GET /health`  
  Returns service health and pod hostname.
  Example response:
  ```json
  {
    "status": "healthy",
    "pod": "hostname-or-pod-name"
  }
  ```

## Local Development

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install pytest
```

### 3. Run the app

```bash
python app.py
```

App runs at `http://localhost:8080`.

### 4. Run tests

```bash
PYTHONPATH=. pytest -q
```

## Run with Docker

Build image:

```bash
docker build -t erricson-ibm-poc:local .
```

Run container:

```bash
docker run --rm -p 8080:8080 erricson-ibm-poc:local
```

The container starts Gunicorn on port `8080`.

## CI/CD Workflow Details

Workflow file: `.github/workflows/main.yml`

### Jobs

1. `test`
- Checks out code
- Sets up Python
- Installs dependencies
- Runs pytest

2. `sonar`
- Depends on `test`
- Runs SonarCloud scan using `SONAR_TOKEN`

3. `fortify`
- Depends on `test`
- Executes `fortify_scan.sh`
- Uses `FORTIFY_SCA_IMAGE` when provided

4. `build-image`
- Depends on `sonar` and `fortify`
- Authenticates to GCP using Workload Identity Federation
- Triggers Cloud Build
- Waits for successful build
- Reads pushed image digest from Artifact Registry

5. `sign-image`
- Depends on `build-image`
- Creates Binary Authorization attestation for built digest

6. `update-gitops-repo`
- Depends on `build-image` and `sign-image`
- Checks out separate GitOps repo
- Updates Kustomize `newTag` with digest
- Commits and pushes change

## Required GitHub Secrets

The workflow expects these repository secrets:

- `SONAR_TOKEN`
- `FORTIFY_SCA_IMAGE` (optional if scanner available another way)
- `WIF_PROVIDER`
- `GCP_SERVICE_ACCOUNT`
- `ARTIFACT_REGION`
- `GCP_PROJECT_ID`
- `ARTIFACT_REPO`
- `GITOPS_PAT`

## Sonar Configuration

`sonar-project.properties` contains:
- Project key/name/version
- Source path
- Coverage report path (`coverage.xml`)
- SonarCloud organization and host URL

If coverage is not generated in CI, add a step to run tests with coverage output.

## Fortify Scan Helper

`fortify_scan.sh` behavior:
- If `FORTIFY_SCA_IMAGE` is set, runs scans in Docker
- Otherwise uses local `sourceanalyzer` if installed
- If neither is available, exits gracefully without failing hard

## Troubleshooting

- `ModuleNotFoundError: No module named 'flask'`  
  Install dependencies: `pip install -r requirements.txt`

- `ModuleNotFoundError: No module named 'app'` during tests  
  Run tests from repository root with `PYTHONPATH=. pytest -q`

- Sonar job failing  
  Verify `SONAR_TOKEN` and `sonar-project.properties`

- GCP auth/build failures  
  Verify Workload Identity setup and all GCP-related secrets

- GitOps push fails  
  Ensure `GITOPS_PAT` has repo write access to the target GitOps repository

## Notes

- The project and repo names currently use `Erricson`/`Ericsson` inconsistently. This does not break functionality, but standardizing naming would reduce confusion.
- Runner label `my-gke-runners` implies self-hosted GitHub runners are required for this pipeline.
