import os, json, urllib.request, time

diff_path = os.environ.get("DIFF_PATH", "/tmp/pr_diff.txt")
api_key = os.environ.get("DEEPSEEK_API_KEY", "")
if not api_key:
    print("ERROR: API_KEY env var is empty. Set DEEPSEEK_API_KEY secret in repo settings.")
    exit(1)
pr_number = os.environ["PR_NUMBER"]
token = os.environ["GH_TOKEN"]
repo = os.environ["GITHUB_REPOSITORY"]

api_url = os.environ.get("API_URL", "https://api.deepseek.com/v1/chat/completions")
model = os.environ.get("MODEL", "deepseek-chat")

with open(diff_path) as f:
    diff = f.read()

if len(diff) < 50:
    print("Diff too small, skipping review")
    exit(0)

payload = {
    "model": model,
    "messages": [
        {"role": "system", "content": "You are a senior code reviewer. Review pull request diffs for bugs, security issues, and code quality problems. Be concise."},
        {"role": "user", "content": f"Review this pull request diff:\n\n{diff[:30000]}"}
    ],
    "temperature": 0.3
}

data = json.dumps(payload).encode()
req = urllib.request.Request(api_url, data=data, headers={
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
})

review = None
for attempt in range(5):
    try:
        resp = json.loads(urllib.request.urlopen(req).read())
        review = resp["choices"][0]["message"]["content"]
        break
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"API error: {e.code} {e.reason} — {body[:500]}")
        if e.code == 429 and attempt < 4:
            wait = min(30, 2 ** attempt * 5)
            print(f"Rate limited, retrying in {wait}s...")
            time.sleep(wait)
        else:
            review = "_Automated review skipped: AI API unavailable._"
            break
    except Exception as e:
        print(f"Unexpected error: {e}")
        review = "_Automated review skipped: unexpected error._"
        break

comment_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
comment_payload = json.dumps({"body": f"## AI Code Review\n\n{review}"}).encode()
comment_req = urllib.request.Request(comment_url, data=comment_payload, headers={
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
})
urllib.request.urlopen(comment_req)
print("Review posted successfully")
