---
on:
  workflow_dispatch:
  pull_request:
    types: [opened, synchronize]
permissions:
  contents: read
  pull-requests: read
network: defaults
safe-outputs:
  create-pull-request:
    max: 1
---

# Test agent

You are a test agent for a Python project. Ensure the test command
`pytest || true` passes. If tests are missing for changed code, add them. If they
fail, fix the code (not the tests) and open a PR. Do not push to main.
