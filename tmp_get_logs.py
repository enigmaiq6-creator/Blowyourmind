import json, urllib.request, os, sys

token = os.popen("gh auth token").read().strip()

# Get job steps
req = urllib.request.Request(
    "https://api.github.com/repos/enigmaiq6-creator/Blowyourmind/actions/jobs/82844312530",
    headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
)
data = json.loads(urllib.request.urlopen(req).read())

# Find the what_if step number
for s in data['steps']:
    if 'What If' in s['name']:
        step_number = s['number']
        step_name = s['name']
        print(f"What If step: #{step_number} - {step_name}")
        print(f"  Status: {s['status']}, started_at: {s.get('started_at','?')}")
        break

# Try to get the log download URL for the run
run_id = "27991370616"
req2 = urllib.request.Request(
    f"https://api.github.com/repos/enigmaiq6-creator/Blowyourmind/actions/runs/{run_id}",
    headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
)
run_data = json.loads(urllib.request.urlopen(req2).read())
print(f"\nRun status: {run_data['status']}, conclusion: {run_data['conclusion']}")
print(f"Run created: {run_data['created_at']}")
print(f"Run updated: {run_data['updated_at']}")

# The logs_url points to the archive
print(f"\nLogs URL: {run_data.get('logs_url')}")
print(f"Jobs URL: {run_data.get('jobs_url')}")

# Since we can't get live logs via API, let's check the timeline
req3 = urllib.request.Request(
    f"https://api.github.com/repos/enigmaiq6-creator/Blowyourmind/actions/runs/{run_id}/timeline",
    headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
)
try:
    timeline = json.loads(urllib.request.urlopen(req3).read())
    print(f"\nTimeline entries: {len(timeline)}")
    for entry in timeline[:5]:
        print(f"  {entry.get('actor',{}).get('login','?')}: {entry.get('event','?')} at {entry.get('created_at','?')}")
except Exception as e:
    print(f"\nTimeline not available: {e}")

# Print full step info
print(f"\n=== ALL STEPS ===")
for s in data['steps']:
    t = s['completed_at'] or "RUNNING"
    print(f"  [{s['status']:>8}] #{s['number']:2d} {s['name']}")
    print(f"       started: {s['started_at']}")
    if s['completed_at']:
        print(f"       finished: {s['completed_at']}")
