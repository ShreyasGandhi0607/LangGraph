#!/bin/bash
set -e

echo "Starting token expiry email workflow..."

# Load token expiry calculation
source pipelines/ci-email/token_expiry_check.sh

# Exit early if notification is not required
if [[ "$SHOULD_NOTIFY" != "true" && "$FORCE_EMAIL_SEND" != "true" ]]; then
  echo "No email required today"
  exit 0
fi

# Load payload builder and SES sender
source pipelines/ci-email/email_payload_data.sh
source pipelines/ci-email/aws_ses_send_email.sh

# ----------------------------
# Email payload configuration
# ----------------------------

declare -A DYNAMIC_PROPERTIES=(
  ["flowType"]="TOKEN_EXPIRY"
  ["daysLeft"]="$DAYS_LEFT"
  ["tokenCreatedAt"]="$REFRESH_TOKEN_CREATED_AT"
)

declare -A EMAIL_CONFIG=(
  ["TO"]="$TOKEN_EXPIRY_EMAIL_TO"
  ["FROM"]="no-reply@code.roche.com"
  ["SUBJECT"]="⚠ Refresh token expires in $DAYS_LEFT days"
)

# ----------------------------
# Safety + visibility logs
# ----------------------------

echo "Email details:"
echo "  FROM: ${EMAIL_CONFIG[FROM]}"
echo "  TO:   ${EMAIL_CONFIG[TO]}"
echo "  SUBJECT: ${EMAIL_CONFIG[SUBJECT]}"
echo "  DAYS_LEFT: $DAYS_LEFT"
echo "  TOKEN_CREATED_AT: $REFRESH_TOKEN_CREATED_AT"

# SES sandbox warning (important)
if [[ "${EMAIL_CONFIG[TO]}" != *@code.roche.com ]]; then
  echo "WARNING: External email detected."
  echo "SES sandbox may block delivery unless recipient is verified."
fi

# ----------------------------
# Generate payload and send
# ----------------------------

rocheGenerate_payloadFunction DYNAMIC_PROPERTIES EMAIL_CONFIG
rochePipeline_awsSesSendEmailFunction

echo "Email send flow completed successfully"