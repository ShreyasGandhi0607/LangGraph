#!/bin/bash
set -e

# Refresh token validity
EXPIRY_DAYS=30
REMIND_DAYS=(9 7 5 3 1)

# Convert creation date to epoch
CREATED_EPOCH=$(date -u -d "$REFRESH_TOKEN_CREATED_AT" +%s)
NOW_EPOCH=$(date -u +%s)

# Calculate days passed and left
DAYS_PASSED=$(( (NOW_EPOCH - CREATED_EPOCH) / 86400 ))
DAYS_LEFT=$(( EXPIRY_DAYS - DAYS_PASSED ))

# Export for other scripts
export DAYS_LEFT
export SHOULD_NOTIFY="false"

for d in "${REMIND_DAYS[@]}"; do
  if [[ "$DAYS_LEFT" -eq "$d" ]]; then
    export SHOULD_NOTIFY="true"
  fi
done

echo "Refresh token days left: $DAYS_LEFT"