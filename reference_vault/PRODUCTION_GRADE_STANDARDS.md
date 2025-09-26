
# Production Grade Standards

## Logging
- Levels: trace/debug/info/warn/error.
- Fields: timestamp, level, service, trace_id, span_id, event, status, context.
- No secrets.

## Error Handling
- Record in structured objects; adapt endlessly until goal (e.g., root success).
- Fallback: Brute-force next exploit path.

## Dependency Pinning
- Exact versions (e.g., Magisk v27.0).

References:
- None (internal logic only)
