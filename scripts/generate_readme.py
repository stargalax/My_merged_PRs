from collections import Counter
import json

with open("output/prs.json", encoding="utf-8") as f:
    prs = json.load(f)

merged = [pr for pr in prs if pr["state"] == "MERGED"]

repo_counts = Counter(pr["repository"]["owner"] for pr in merged)

repos = {}

for pr in merged:
    repo = pr["repository"]["owner"]

    repos.setdefault(repo, []).append(pr)

total_additions = sum(pr["additions"] for pr in merged)
total_deletions = sum(pr["deletions"] for pr in merged)

lines = []

lines.append("#  My Open Source Contributions\n")
lines.append("> Automatically updated with GitHub Actions.\n")

lines.append("## Stats\n")

lines.append("| Metric | Value |")
lines.append("|---|---:|")
lines.append(f"| Merged PRs | **{len(merged)}** |")
lines.append(f"| Repositories | **{len(repos)}** |")
lines.append(f"| Total Additions | **{total_additions:,}** |")
lines.append(f"| Total Deletions | **{total_deletions:,}** |")
lines.append("")

lines.append("## ✍️(◔◡◔) Top Repositories\n")

lines.append("| Repository | PRs |")
lines.append("|---|---:|")

for repo, count in repo_counts.most_common(10):
    lines.append(f"| {repo} | {count} |")

lines.append("")

lines.append("## (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ Recently Merged\n")

for pr in merged[:10]:
    lines.append(
        f"- **{pr['repository']['owner']}** "
        f"[#{pr['number']}]({pr['url']}) — {pr['title']}"
    )

lines.append("")

lines.append("# (〃￣︶￣)人(￣︶￣〃) All Contributions\n")

for repo in sorted(repos):

    sample = repos[repo][0]

    stars = sample["repository"]["stars"]
    language = sample["repository"]["language"]

    lines.append(f"## {repo}")
    lines.append("")
    lines.append(f"⭐ {stars:,} stars • {language}")
    lines.append("")

    for pr in repos[repo]:
        lines.append(
            f"-  [#{pr['number']}]({pr['url']}) — {pr['title']}"
        )

    lines.append("")

with open("README.md", "w", encoding="utf-8") as f:

    f.write("\n".join(lines))
