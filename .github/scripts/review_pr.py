import os, json, urllib.request, time

diff_path = os.environ.get("DIFF_PATH", "/tmp/pr_diff.txt")
api_key = os.environ["GEMINI_API_KEY"]
pr_number = os.environ["PR_NUMBER"]
token = os.environ["GH_TOKEN"]
repo = os.environ["GITHUB_REPOSITORY"]

with open(diff_path) as f:
    diff = f.read()

if len(diff) < 50:
    print("Diff too small, skipping review")
    exit(0)

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={api_key}"
payload = {
    "contents": [{
        "parts": [{"text": f"Review this pull request diff. Check for bugs, code quality issues, security problems, and suggest improvements. Be concise.\n\n{diff[:30000]}"}]
    }]
}

data = json.dumps(payload).encode()
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

review = None
for attempt in range(5):
    try:
        resp = json.loads(urllib.request.urlopen(req).read())
        review = resp["candidates"][0]["content"]["parts"][0]["text"]
        break
    except urllib.error.HTTPError as e:
        if e.code == 429 and attempt < 4:
            wait = min(30, 2 ** attempt * 5)
            print(f"Rate limited, retrying in {wait}s...")
            time.sleep(wait)
        else:
            print(f"Gemini API error: {e.code} {e.reason}")
            review = "_Automated review skipped: AI API rate limited._"
            break

comment_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
comment_payload = json.dumps({"body": f"## AI Code Review\n\n{review}"}).encode()
comment_req = urllib.request.Request(comment_url, data=comment_payload, headers={
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
})
urllib.request.urlopen(comment_req)
print("Review posted successfully")
