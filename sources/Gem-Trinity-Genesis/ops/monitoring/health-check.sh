#!/bin/bash

# Health Check Script for Gem Trinity Genesis
# This script checks if the backend is healthy and sends alerts if not
# Usage: ./ops/monitoring/health-check.sh

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
HEALTH_ENDPOINT="/api/health/detailed"
ALERT_EMAIL="${ALERT_EMAIL:-}"  # Set your email for alerts
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"  # Set your Slack webhook URL
CHECK_TIMEOUT=10

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Checking Gem Trinity Genesis health..."
echo "URL: ${BACKEND_URL}${HEALTH_ENDPOINT}"

# Make health check request
response=$(curl -s -w "\n%{http_code}" "${BACKEND_URL}${HEALTH_ENDPOINT}" --max-time $CHECK_TIMEOUT 2>/dev/null)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    # Parse JSON response (basic parsing with grep/sed)
    status=$(echo "$body" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

    case "$status" in
        "healthy")
            echo -e "${GREEN}✓ System is healthy${NC}"
            exit 0
            ;;
        "degraded")
            echo -e "${YELLOW}⚠ System is degraded${NC}"
            echo "$body" | grep -o '"issues":\[[^]]*\]' | sed 's/"issues"://; s/\[//; s/\]//; s/"//g'
            # Send alert for degraded state
            send_alert "WARNING: Gem Trinity Genesis is degraded" "$body"
            exit 1
            ;;
        *)
            echo -e "${RED}✗ Unknown status: $status${NC}"
            send_alert "ERROR: Gem Trinity Genesis unknown status" "$body"
            exit 2
            ;;
    esac
else
    echo -e "${RED}✗ Health check failed (HTTP $http_code)${NC}"
    message="Backend is not responding (HTTP $http_code)"
    send_alert "CRITICAL: Gem Trinity Genesis is DOWN" "$message"
    exit 3
fi

# Function to send alerts
send_alert() {
    local title="$1"
    local message="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Send email if configured
    if [ -n "$ALERT_EMAIL" ]; then
        echo "$message" | mail -s "$title" "$ALERT_EMAIL"
        echo "📧 Email alert sent to $ALERT_EMAIL"
    fi

    # Send Slack notification if configured
    if [ -n "$SLACK_WEBHOOK" ]; then
        slack_payload "{\"text\":\"*$title*\n\n$message\n\nTimestamp: $timestamp\"}"
        curl -s -X POST -H 'Content-type: application/json' --data "$slack_payload" "$SLACK_WEBHOOK" > /dev/null
        echo "💬 Slack alert sent"
    fi

    # Log to file
    mkdir -p logs
    echo "[$timestamp] $title: $message" >> logs/health-check-alerts.log
}
