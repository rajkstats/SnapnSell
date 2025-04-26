#!/bin/bash
set -e

# Configuration
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="snap-and-sell"
REGION="asia-south1"  # Mumbai region, change if needed

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Deploying Snap & Sell to Google Cloud Run...${NC}"

# Build the container image
echo -e "${GREEN}Building container image...${NC}"
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
echo -e "${GREEN}Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="OPENAI_API_KEY=${OPENAI_API_KEY}"

echo -e "${GREEN}Deployment completed!${NC}"
echo -e "Your app will be available at the URL shown above."
