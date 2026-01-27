#!/bin/bash
set -e

source ci-email/token_expiry_check.sh

if [[ "$SHOULD_NOTIFY" != "true" ]]; then
  echo "No email required today"
  exit 0
fi

source ci-email/email_payload_data.sh
source ci-email/aws_ses_send_email.sh

declare -A DYNAMIC_PROPERTIES=(
  ["flowType"]="TOKEN_EXPIRY"
  ["daysLeft"]="$DAYS_LEFT"
  ["tokenCreatedAt"]="$REFRESH_TOKEN_CREATED_AT"
)

declare -A EMAIL_CONFIG=(
  ["TO"]="dev@company.com"
  ["SUBJECT"]="⚠️ Refresh token expires in $DAYS_LEFT days"
)

rocheGenerate_payloadFunction DYNAMIC_PROPERTIES EMAIL_CONFIG
rochePipeline_awsSesSendEmailFunction