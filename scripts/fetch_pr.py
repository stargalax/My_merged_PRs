import json
import os
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("GITHUB_USERNAME")
TOKEN = os.getenv("GITHUB_TOKEN")

GRAPHQL_URL = "https://api.github.com/graphql"

QUERY = """
query($cursor: String, $query: String!) {
  search(
    query: $query,
    type: ISSUE,
    first: 50,
    after: $cursor
  ) {
    pageInfo {
      hasNextPage
      endCursor
    }

    nodes {
      ... on PullRequest {

        id
        number
        title
        url

        state

        createdAt
        mergedAt
        closedAt

        additions
        deletions
        changedFiles

        repository {
          name
          nameWithOwner
          url

          stargazerCount
          forkCount

          primaryLanguage {
            name
          }

          repositoryTopics(first: 10) {
            nodes {
              topic {
                name
              }
            }
          }
        }
      }
    }
  }
}
"""

headers = {
    "Authorization": f"Bearer {TOKEN}"
}


def run_query(cursor=None):

    variables = {
        "cursor": cursor,
        # "query": f"author:{USERNAME} is:pr"
        "query": f"author:{USERNAME} is:pr is:merged"

    }

    r = requests.post(
        GRAPHQL_URL,
        json={
            "query": QUERY,
            "variables": variables
        },
        headers=headers,
    )

    r.raise_for_status()

    result = r.json()

    if "errors" in result:
        raise Exception(result["errors"])

    return result["data"]


all_prs = []

cursor = None

while True:

    data = run_query(cursor)

    search = data["search"]

    for pr in search["nodes"]:

        topics = []

        for topic in pr["repository"]["repositoryTopics"]["nodes"]:
            topics.append(topic["topic"]["name"])

        all_prs.append(
            {
                "title": pr["title"],
                "number": pr["number"],
                "url": pr["url"],
                "state": pr["state"],
                "createdAt": pr["createdAt"],
                "mergedAt": pr["mergedAt"],
                "closedAt": pr["closedAt"],
                "additions": pr["additions"],
                "deletions": pr["deletions"],
                "changedFiles": pr["changedFiles"],
                "repository": {
                    "name": pr["repository"]["name"],
                    "owner": pr["repository"]["nameWithOwner"],
                    "url": pr["repository"]["url"],
                    "stars": pr["repository"]["stargazerCount"],
                    "forks": pr["repository"]["forkCount"],
                    "language": (
                        pr["repository"]["primaryLanguage"]["name"]
                        if pr["repository"]["primaryLanguage"]
                        else None
                    ),
                    "topics": topics,
                },
            }
        )

    page = search["pageInfo"]

    if not page["hasNextPage"]:
        break

    cursor = page["endCursor"]


all_prs.sort(
    key=lambda x: (
        x["mergedAt"] or "",
        x["createdAt"]
    ),
    reverse=True,
)

os.makedirs("output", exist_ok=True)

with open("output/prs.json", "w") as f:
    json.dump(all_prs, f, indent=4)

print(f"Fetched {len(all_prs)} pull requests.")