#!/bin/bash
set -e

EXPIRY_DAYS=30
REMIND_DAYS=(21 7 5 3 1)

if [[ -z "$REFRESH_TOKEN_CREATED_AT" ]]; then
  echo "REFRESH_TOKEN_CREATED_AT is not set"
  exit 1
fi

CREATED_EPOCH=$(date -u -d "$REFRESH_TOKEN_CREATED_AT" +%s)
NOW_EPOCH=$(date -u +%s)

if (( CREATED_EPOCH > NOW_EPOCH )); then
  DAYS_PASSED=0
else
  DAYS_PASSED=$(( (NOW_EPOCH - CREATED_EPOCH) / 86400 ))
fi

DAYS_LEFT=$(( EXPIRY_DAYS - DAYS_PASSED ))

export DAYS_LEFT
export SHOULD_NOTIFY="false"

for d in "${REMIND_DAYS[@]}"; do
  if [[ "$DAYS_LEFT" -eq "$d" ]]; then
    SHOULD_NOTIFY="true"
    break
  fi
done

export SHOULD_NOTIFY

echo "Refresh token days left: $DAYS_LEFT"