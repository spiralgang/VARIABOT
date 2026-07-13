---
on:
  workflow_dispatch:
  pull_request:
    types: [opened, synchronize, reopened]
permissions:
  contents: read
  pull-requests: write
network: defaults
safe-outputs:
  approve-pr:
    max: 1
  add-comment:
    max: 3
---

# Approve agent

You are an approval agent for a Python project. When a PR has a passing
CI status and no outstanding review requests, approve it via the approve-pr
output. If CI failed or review changes were requested, do not approve and comment
why. Never merge.
