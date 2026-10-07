#!/usr/bin/env bash
# Walks the spec §23 demo scenario against a RUNNING server over real HTTP.
#
#   API_BASE=http://localhost:8000/api ./scripts/demo_walkthrough.sh
#
# Requires: curl, python3.
set -euo pipefail

API="${API_BASE:-http://localhost:8000/api}"
EMAIL="demo-$(date +%s)@example.com"
PASSWORD="DemoPass123"

green() { printf '\033[92m%s\033[0m\n' "$1"; }
step() { printf '\n\033[1m%s\033[0m\n' "$1"; }
jqp() { python3 -c "import sys,json;d=json.load(sys.stdin);print(eval(sys.argv[1],{'d':d}))" "$1"; }

step "1. Register $EMAIL"
TOKEN=$(curl -fsS -X POST "$API/auth/register" -H 'Content-Type: application/json' \
  -d "{\"name\":\"Demo User\",\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" | jqp "d['access_token']")
green "  token acquired (${#TOKEN} chars)"
AUTH="Authorization: Bearer $TOKEN"

step "2. Log in"
curl -fsS -X POST "$API/auth/login" -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" >/dev/null
green "  login ok"
green "  /auth/me -> $(curl -fsS "$API/auth/me" -H "$AUTH" | jqp "d['email']")"

step "3. Dashboard: list agents"
curl -fsS "$API/agents" -H "$AUTH" \
  | python3 -c "import sys,json;[print(f\"  {a['agent_type']:<10} {a['profile_status']}\") for a in json.load(sys.stdin)]"

step "4-5. Select Marketing -> does a profile exist?"
curl -fsS "$API/profile/marketing" -H "$AUTH" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(f\"  exists={d['exists']} status={d['status_label']}\")"

step "6. Setup questions served by the API"
curl -fsS "$API/agents/marketing" -H "$AUTH" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print('  '+d['setup_headline']);[print(f\"    - {f['label']}: {', '.join(f['options'][:4]) or f['kind']}\") for f in d['profile_fields']]"

step "7-8. Save the Marketing profile (LinkedIn / Professional / Short / Businesses)"
curl -fsS -X POST "$API/profile/marketing" -H "$AUTH" -H 'Content-Type: application/json' -d '{
  "profile_data": {
    "platforms": ["LinkedIn"],
    "brand": "Acme Cloud",
    "audience": ["Businesses"],
    "tone": "Professional",
    "content_style": "Short",
    "goals": "Lead generation"
  }}' | python3 -c "import sys,json;d=json.load(sys.stdin);print(f\"  saved: configured={d['is_configured']}\")"

step "9-11. Ask for a LinkedIn post"
RESP=$(curl -fsS -X POST "$API/chat" -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"message":"Create a LinkedIn post about AI automation.","agent_type":"marketing"}')
echo "$RESP" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"  routed to: {d['routing']['selected_agent']} via {d['routing']['source']}\")
print(f\"  latency: {d['latency_ms']} ms · provider: {d['personalization']['provider']}\")
print('  global profile used:')
[print(f'    - {line}') for line in d['personalization']['global_profile_summary'][:4]]
print('  marketing profile used:')
[print(f'    - {line}') for line in d['personalization']['agent_profile_summary'][:4]]
print('  --- response (first 400 chars) ---')
print('  ' + d['assistant_message']['content'][:400].replace('\n', '\n  '))
"
MSG_ID=$(echo "$RESP" | jqp "d['assistant_message']['id']")
CONV_ID=$(echo "$RESP" | jqp "d['conversation_id']")

step "12-13. Feedback: \"Make future posts more concise.\""
curl -fsS -X POST "$API/feedback" -H "$AUTH" -H 'Content-Type: application/json' \
  -d "{\"message_id\":\"$MSG_ID\",\"rating\":-1,\"feedback_text\":\"Make future posts more concise.\"}" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(f\"  memories created: {d['memories_created']}\");print(f\"  profile updated (should be False on first signal): {d['profile_updated']}\")"

step "14-15. New Marketing conversation reuses the learned preference"
curl -fsS -X POST "$API/chat" -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"message":"Write a LinkedIn post about cutting cloud costs.","agent_type":"marketing"}' \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('  memories retrieved into context:')
[print(f\"    - [{'standing' if m['pinned'] else 'recalled'}] {m['content']} (rel {m['similarity']:.2f})\") for m in d['personalization']['memories_used']]
"

step "16-17. Switch to the Technical Agent: a different profile is loaded"
curl -fsS -X POST "$API/profile/technical" -H "$AUTH" -H 'Content-Type: application/json' -d '{
  "profile_data": {
    "skills": ["Backend"], "programming_languages": ["Python"],
    "difficulty_level": "Intermediate", "coding_preferences": ["Code examples"],
    "frameworks": ["FastAPI"]
  }}' >/dev/null
curl -fsS -X POST "$API/chat" -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"message":"Explain Python decorators","agent_type":"technical"}' \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('  technical profile used:')
[print(f'    - {line}') for line in d['personalization']['agent_profile_summary']]
"

step "Router agent with NO explicit selection"
for q in "Explain Python decorators" "Create a LinkedIn post about AWS" \
         "Improve my resume for a software engineer role" "Explain photosynthesis for class 10" \
         "Analyze this sales dataset" "Find information about RAG architecture" \
         "Write a short sci-fi story"; do
  printf '  %-48s -> ' "$q"
  curl -fsS -X POST "$API/chat" -H "$AUTH" -H 'Content-Type: application/json' \
    -d "$(python3 -c "import json,sys;print(json.dumps({'message':sys.argv[1]}))" "$q")" \
    | jqp "d['routing']['selected_agent'] + ' (' + d['routing']['source'] + ')'"
done

step "Conversation history"
curl -fsS "$API/conversations" -H "$AUTH" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(f'  {len(d)} conversations');[print(f\"    [{c['agent_type']}] {c['title']}\") for c in d[:6]]"
curl -fsS "$API/conversations?agent_type=marketing" -H "$AUTH" \
  | python3 -c "import sys,json;print(f'  filtered by marketing: {len(json.load(sys.stdin))}')"

step "Memory store"
curl -fsS "$API/memory/summary" -H "$AUTH" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(f\"  total={d['total']} by_agent={d['by_agent']}\")"

step "Dashboard stats"
curl -fsS "$API/dashboard/stats" -H "$AUTH" | python3 -m json.tool | sed 's/^/  /'

step "Cleanup"
curl -fsS -X DELETE "$API/conversations/$CONV_ID" -H "$AUTH" -o /dev/null -w '  delete conversation -> HTTP %{http_code}\n'

echo
green "Demo walkthrough complete."
