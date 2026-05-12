#!/usr/bin/env bash
# Call the deployed KYC onboarding agent app via CLI (OAuth).
#
# Usage:
#   ./call_app.sh "Your message here"
#   ./call_app.sh --thread-id <id> "Follow-up message"
#   THREAD_ID=<id> ./call_app.sh "Follow-up message"
#
# The script prints the thread_id from the response so you can copy-paste it
# for follow-up calls. Example multi-turn conversation:
#
#   $ bash call_app.sh "Hi, I'd like to open an account"
#   # ... thread_id: abc-123 ...
#   $ bash call_app.sh --thread-id abc-123 "Dirk van Dijk"
#   # ... agent remembers context ...
#
# Env vars:
#   DATABRICKS_PROFILE  - CLI profile for auth (e.g. fevm-demo)
#   DATABRICKS_TOKEN    - OAuth or PAT token (skips CLI auth)
#   APP_NAME            - App name (default: kyc-onboarding-agent)
#   APP_URL             - Full app URL (skips CLI lookup if set)
#   THREAD_ID           - Conversation thread (alternative to --thread-id flag)
#   STREAM              - true (default) or false
#   CURL_VERBOSE        - set to 1 for curl -v output
#
# See: https://docs.databricks.com/aws/en/generative-ai/agent-framework/author-agent

APP_NAME="${APP_NAME:-kyc-onboarding-agent}"
APP_URL="${APP_URL:-}"

# --- Parse arguments ---
THREAD_ID="${THREAD_ID:-}"
MSG=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --thread-id|-t)
      THREAD_ID="$2"; shift 2 ;;
    --app-name|-a)
      APP_NAME="$2"; shift 2 ;;
    --app-url)
      APP_URL="$2"; shift 2 ;;
    *)
      MSG="$1"; shift ;;
  esac
done
MSG="${MSG:-Hi, I want to open a Personal Current Account.}"

# --- Auth ---
AUTH_OPTS=()
[ -n "${DATABRICKS_PROFILE}" ] && AUTH_OPTS=(--profile "$DATABRICKS_PROFILE")

TOKEN="${DATABRICKS_TOKEN:-}"
if [ -z "$TOKEN" ]; then
  RAW=$(databricks auth token "${AUTH_OPTS[@]}" 2>/dev/null)
  if command -v jq >/dev/null 2>&1 && echo "$RAW" | jq -e '.access_token' >/dev/null 2>&1; then
    TOKEN=$(echo "$RAW" | jq -r '.access_token')
  else
    TOKEN=$(echo "$RAW" | tr -d '\n\r')
    [ -n "$TOKEN" ] && [ "${#TOKEN}" -lt 30 ] && TOKEN=""
  fi
fi
if [ -z "$TOKEN" ]; then
  if command -v jq >/dev/null 2>&1; then
    T=$(databricks auth env "${AUTH_OPTS[@]}" 2>/dev/null | jq -r '.env.DATABRICKS_TOKEN // empty')
    [ -n "$T" ] && TOKEN="$T"
  fi
fi
if [ -z "$TOKEN" ]; then
  echo "No token found. Do one of:"
  echo "  1. databricks auth login --host https://<workspace>.cloud.databricks.com"
  echo "     export DATABRICKS_PROFILE=<profile>"
  echo "  2. export DATABRICKS_TOKEN=\$(databricks auth token --profile \$DATABRICKS_PROFILE)"
  exit 1
fi

# --- Resolve APP_URL if not set (lookup via Databricks CLI) ---
if [ -z "$APP_URL" ]; then
  APP_URL=$(databricks apps get "$APP_NAME" "${AUTH_OPTS[@]}" -o json 2>/dev/null | jq -r '.url // empty')
fi
if [ -z "$APP_URL" ]; then
  echo "Could not resolve app URL for '$APP_NAME'."
  echo "Set APP_URL, APP_NAME, or use --app-url / --app-name flags."
  exit 1
fi
echo "App: $APP_NAME ($APP_URL)"

# --- Build request body ---
INVOKE_URL="${APP_URL}/invocations"
STREAM="${STREAM:-true}"

if [ -n "$THREAD_ID" ]; then
  BODY=$(jq -n \
    --arg msg "$MSG" \
    --argjson stream "$STREAM" \
    --arg tid "$THREAD_ID" \
    '{input: [{role: "user", content: $msg}], stream: $stream, custom_inputs: {thread_id: $tid}}')
else
  BODY=$(jq -n \
    --arg msg "$MSG" \
    --argjson stream "$STREAM" \
    '{input: [{role: "user", content: $msg}], stream: $stream}')
fi

# --- Call the agent ---
BODY_FILE=$(mktemp)
trap 'rm -f "$BODY_FILE"' EXIT

CURL_ARGS=(-s -w "%{http_code}" -o "$BODY_FILE" -X POST "$INVOKE_URL" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "$BODY")
[ -n "${CURL_VERBOSE}" ] && CURL_ARGS=(-v "${CURL_ARGS[@]}")

HTTP_CODE=$(curl "${CURL_ARGS[@]}")

# --- Parse response ---
if [ -s "$BODY_FILE" ]; then
  if command -v jq >/dev/null 2>&1; then
    # Extract reply text
    REPLY=$(jq -r '.output[]? | .content[]? | select(.type == "output_text") | .text' "$BODY_FILE" 2>/dev/null | head -1)
    if [ -z "$REPLY" ]; then
      # Streaming: parse SSE data lines
      REPLY=$(sed -n 's/^data: //p' "$BODY_FILE" | while read -r line; do
        [ "$line" = "[DONE]" ] && break
        jq -r '.item.content[]? | select(.type == "output_text") | .text' 2>/dev/null <<< "$line"
      done | head -1)
    fi

    # Extract thread_id from non-streaming or streaming response
    RESP_THREAD_ID=$(jq -r '.custom_outputs.thread_id // empty' "$BODY_FILE" 2>/dev/null)
    if [ -z "$RESP_THREAD_ID" ]; then
      # Streaming: look for thread_id in SSE data lines
      RESP_THREAD_ID=$(sed -n 's/^data: //p' "$BODY_FILE" | while read -r line; do
        [ "$line" = "[DONE]" ] && break
        jq -r '.item.custom_outputs.thread_id // empty' 2>/dev/null <<< "$line"
      done | grep -v '^$' | head -1)
    fi

    if [ -n "$REPLY" ]; then
      echo ""
      echo "--- Agent reply ---"
      echo "$REPLY"
    elif grep -q '"output": \[\]' "$BODY_FILE" 2>/dev/null || [ "$(cat "$BODY_FILE")" = "{}" ]; then
      echo ""
      echo "(Empty output. The app may be running without Spark or the response format differs.)"
    fi

    echo ""
    if [ -n "$RESP_THREAD_ID" ]; then
      echo "--- thread_id: $RESP_THREAD_ID ---"
      echo ""
      echo "Continue this conversation:"
      echo "  bash agents/kyc_agent/call_app.sh --thread-id $RESP_THREAD_ID \"Your next message\""
    fi
  else
    cat "$BODY_FILE"
  fi
else
  echo "(empty body)"
fi
echo ""
echo "--- HTTP $HTTP_CODE ---"

# Hints on auth errors
if [ "$HTTP_CODE" = "401" ]; then
  echo "401 = Unauthorized. Use OAuth: databricks auth login, set DATABRICKS_PROFILE."
elif [ "$HTTP_CODE" = "302" ]; then
  echo "302 = redirect. Use OAuth from 'databricks auth login'. Run with CURL_VERBOSE=1 to see Location."
fi
