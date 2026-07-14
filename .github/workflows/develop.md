---
on:
  workflow_dispatch:
  issues:
    types: [opened]
permissions:
  contents: read
  issues: read
  pull-requests: read
network: defaults
safe-outputs:
  create-pull-request:
    max: 2
---

# Development agent

You are a development agent for a Python project. When a feature issue
is opened, implement it in the codebase following the repo's existing patterns.
Open a pull request that references the issue. Keep changes scoped. Do not merge.
