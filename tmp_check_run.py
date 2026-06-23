import json, urllib.request, os, sys

token = os.popen("gh auth token").read().strip()
job_id = "82844312530"

req = urllib.request.Request(
    f"https://api.github.com/repos/enigmaiq6-creator/Blowyourmind/actions/jobs/{job_id}",
    headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
)
data = json.loads(urllib.request.urlopen(req).read())
steps = data.get('steps', [])
print(f"Job status: {data.get('status')}, conclusion: {data.get('conclusion')}")
for s in steps:
    t = s['completed_at'] or "RUNNING"
    print(f"  [{s['status']:>7}] {s['number']}. {s['name']}")

# Try to get the log for the what_if step
run_id = "27991370616"
req2 = urllib.request.Request(
    f"https://api.github.com/repos/enigmaiq6-creator/Blowyourmind/actions/runs/{run_id}/attempts/1/logs",
    headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
)
try:
    resp = urllib.request.urlopen(req2)
    print(f"\nLogs archive: {resp.geturl()}")
    print(f"Logs size: {resp.length} bytes")
except Exception as e:
    print(f"\nLogs not available yet: {e}")

# Try to get the step logs directly via the steps endpoint
req3 = urllib.request.Request(
    f"https://api.github.com/repos/enigmaiq6-creator/Blowyourmind/actions/jobs/{job_id}/logs",
    headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
)
try:
    resp = urllib.request.urlopen(req3)
    print(f"\nJob log URL: {resp.geturl()}")
    log_text = resp.read().decode('utf-8')
    # Print last 50 lines
    lines = log_text.split('\n')
    print(f"\n--- LAST 50 LINES OF JOB LOG ({len(lines)} total) ---")
    for line in lines[-50:]:
        print(line)
except Exception as e:
    print(f"\nJob log not available: {e}")
