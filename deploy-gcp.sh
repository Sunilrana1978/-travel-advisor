#!/usr/bin/env bash
# deploy-gcp.sh — Full GCP setup + Cloud Run deployment for Travel Advisor ADK
#
# Usage:
#   chmod +x deploy-gcp.sh
#   ./deploy-gcp.sh --project YOUR_PROJECT_ID --api-key YOUR_GOOGLE_API_KEY

set -euo pipefail

REGION="us-central1"
BACKEND_SVC="travel-advisor-backend"
FRONTEND_SVC="travel-advisor-frontend"
SECRET_NAME="GOOGLE_API_KEY"

while [[ $# -gt 0 ]]; do
  case $1 in
    --project)  PROJECT_ID="$2";  shift 2 ;;
    --api-key)  API_KEY="$2";     shift 2 ;;
    --region)   REGION="$2";      shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

[[ -z "${PROJECT_ID:-}" ]] && { echo "❌  --project is required"; exit 1; }
[[ -z "${API_KEY:-}" ]]    && { echo "❌  --api-key is required (get from https://aistudio.google.com/app/apikey)"; exit 1; }

echo ""
echo "🚀  Travel Advisor AI (Google ADK) — GCP Deployment"
echo "   Project : $PROJECT_ID  |  Region: $REGION"
echo ""

gcloud config set project "$PROJECT_ID"

echo "📦  Enabling APIs..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  secretmanager.googleapis.com \
  --quiet

echo "🔐  Storing GOOGLE_API_KEY in Secret Manager..."
echo -n "$API_KEY" | gcloud secrets create "$SECRET_NAME" --data-file=- 2>/dev/null \
  || echo -n "$API_KEY" | gcloud secrets versions add "$SECRET_NAME" --data-file=-

echo "🔑  Configuring IAM..."
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
CR_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${CB_SA}" --role="roles/run.admin" --quiet
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${CB_SA}" --role="roles/iam.serviceAccountUser" --quiet
gcloud secrets add-iam-policy-binding "$SECRET_NAME" \
  --member="serviceAccount:${CR_SA}" --role="roles/secretmanager.secretAccessor" --quiet

echo "🏗️   Submitting Cloud Build..."
gcloud builds submit . \
  --config=cloudbuild.yaml \
  --substitutions="_REGION=${REGION},_BACKEND_SVC=${BACKEND_SVC},_FRONTEND_SVC=${FRONTEND_SVC},_SECRET_NAME=${SECRET_NAME}" \
  --project="$PROJECT_ID"

echo ""
echo "========================================="
BACKEND_URL=$(gcloud run services describe "$BACKEND_SVC" \
  --region="$REGION" --project="$PROJECT_ID" --format='value(status.url)' 2>/dev/null || echo "pending")
FRONTEND_URL=$(gcloud run services describe "$FRONTEND_SVC" \
  --region="$REGION" --project="$PROJECT_ID" --format='value(status.url)' 2>/dev/null || echo "pending")
echo "✅  DEPLOYMENT COMPLETE"
echo ""
echo "  🌐 Frontend  : $FRONTEND_URL"
echo "  ⚙️  Backend   : $BACKEND_URL"
echo "  📖 API Docs  : ${BACKEND_URL}/docs"
echo "  🩺 Health    : ${BACKEND_URL}/health"
echo "========================================="
