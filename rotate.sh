#!/bin/bash
set -e

if [ -z "$NEW_ADP_REFRESH_TOKEN" ]; then
  echo "❌ NEW_ADP_REFRESH_TOKEN is not provided"
  exit 1
fi

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)

echo "Updating ADP_REFRESH_TOKEN..."
curl --fail --silent --request PUT \
  --header "PRIVATE-TOKEN: $GITLAB_API_TOKEN" \
  --form "value=$NEW_ADP_REFRESH_TOKEN" \
  "https://gitlab.com/api/v4/projects/$CI_PROJECT_ID/variables/ADP_REFRESH_TOKEN"

echo "Updating REFRESH_TOKEN_CREATED_AT..."
curl --fail --silent --request PUT \
  --header "PRIVATE-TOKEN: $GITLAB_API_TOKEN" \
  --form "value=$NOW" \
  "https://gitlab.com/api/v4/projects/$CI_PROJECT_ID/variables/REFRESH_TOKEN_CREATED_AT"

echo "✅ Token rotated and creation date updated to $NOW"