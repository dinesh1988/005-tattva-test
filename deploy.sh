#!/bin/bash
# VedAstroPy Google Cloud Run Deployment Script
# Usage: ./deploy.sh [environment]
# Example: ./deploy.sh production

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GCLOUD_PROJECT_ID:-tattva-project}"
SERVICE_NAME="tattva-api"
REGION="${GCLOUD_REGION:-us-central1}"
ENVIRONMENT="${1:-staging}"

echo -e "${GREEN}🚀 Tattva Deployment Script${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: gcloud CLI not found. Please install it first.${NC}"
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Authenticate (if needed)
echo -e "${YELLOW}🔐 Checking authentication...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${YELLOW}Please authenticate:${NC}"
    gcloud auth login
fi

# Set project
echo -e "${YELLOW}📦 Setting project: ${PROJECT_ID}${NC}"
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build version tag
VERSION="v0.6.0-$(date +%Y%m%d-%H%M%S)"
echo -e "${GREEN}📌 Version: ${VERSION}${NC}"

# Deploy to Cloud Run
echo -e "${YELLOW}🚢 Deploying to Cloud Run (${REGION})...${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --source . \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0 \
    --concurrency 80 \
    --set-env-vars "ENVIRONMENT=${ENVIRONMENT},VERSION=${VERSION}" \
    --tag ${ENVIRONMENT}

# Get service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Deployment successful!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Service URL:${NC} ${SERVICE_URL}"
echo -e "${YELLOW}Version:${NC} ${VERSION}"
echo -e "${YELLOW}Environment:${NC} ${ENVIRONMENT}"
echo ""
echo -e "${YELLOW}📊 Test endpoints:${NC}"
echo "  Health: ${SERVICE_URL}/health"
echo "  API Docs: ${SERVICE_URL}/docs"
echo "  Yogas: ${SERVICE_URL}/api/yogas/check"
echo ""
echo -e "${YELLOW}📝 View logs:${NC}"
echo "  gcloud run logs read ${SERVICE_NAME} --region ${REGION} --limit 50"
echo ""
echo -e "${YELLOW}🔍 Monitor service:${NC}"
echo "  https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}"
echo ""
