#!/bin/bash
set -e

source ci-email/email_payload_data.sh
source ci-email/aws_ses_send_email.sh

declare -A DYNAMIC_PROPERTIES=(
  ["flowType"]="TOKEN_ROTATED"
  ["rotatedAt"]="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
)

declare -A EMAIL_CONFIG=(
  ["TO"]="dev@company.com"
  ["SUBJECT"]="✅ ADP Refresh Token Rotated Successfully"
)

rocheGenerate_payloadFunction DYNAMIC_PROPERTIES EMAIL_CONFIG
rochePipeline_awsSesSendEmailFunction