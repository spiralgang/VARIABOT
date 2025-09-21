# Organization Copilot Custom Instructions

## 1. Mission
Accelerate delivery of production-grade, auditable, security-conscious automation, tooling, and documentation. All generated output must:
- Be minimal, composable, and standards-aligned.
- Trace every non-trivial decision to the Reference Vault (`/reference_vault`).
- Avoid duplication: cite vault sections instead of restating them.
- Be merge-ready (no placeholder text, no speculative TODOs unless explicitly tracked).

## 2. Core Principles
1. **Single Source of Truth**: All foundational standards live in `/reference_vault`.
2. **Auditability**: Every file must allow a reviewer to reconstruct rationale from inline minimal notes + end-of-file "References" section.
3. **Least Surface**: No gratuitous abstractions, no premature optimization.
4. **Deterministic Repeatability**: Scripts, infra, and workflows must be reproducible (pin versions, document prerequisites).
5. **Security First**: Never weaken platform protections or provide exploit method steps. High-level design only for privileged contexts.
6. **Progressive Enhancement**: Prefer feature flags / modular composition over monolith additions.
7. **Explicit Contracts**: Each module/function documents inputs, outputs, failure modes, and idempotency assumptions (if applicable).

## 3. Reference Vault Integration
When Copilot proposes code or docs:
- If a rule originates from internal standards: cite as `See: /reference_vault/PRODUCTION_GRADE_STANDARDS.md#<section-slug>`.
- External sources must appear ONLY in end-of-file References (unique, deduplicated).
- Never inline large external excerpts—summarize and cite.
- If a needed standard is missing in the vault: insert a comment `// GAP: propose addition to vault (<short description>)`.

## 4. Coding Standards (Apply to All Languages)

### Structure
- Clear module boundaries with documented APIs
- No circular dependencies
- Fail-fast validation at module entry points
- Consistent error handling patterns (no silent failures)

### Quality Gates
- All functions have docstrings describing purpose, parameters, return values, and exceptions
- No hardcoded values (use constants/config files)
- Input validation for all public interfaces
- Idempotent operations where possible
- Resource cleanup (files, connections, etc.)

### Security Requirements
- Input sanitization for all external data
- Principle of least privilege for file/network access
- No secrets in code or logs
- Secure defaults (opt-in to insecure options)
- Authentication/authorization checks before sensitive operations

### Performance
- O(n) complexity documented for non-trivial algorithms
- Memory usage bounded for batch operations
- Graceful degradation under resource constraints
- Caching strategies documented and invalidation-aware

## 5. File Organization Standards

### Header Template (All Files)
```
# <File Purpose>
# See: /reference_vault/PRODUCTION_GRADE_STANDARDS.md#file-standards
# 
# Dependencies: <list key dependencies>
# Platform: <target platforms>
# Security: <security considerations>
# Performance: <performance characteristics>
```

### Footer Template (All Files)
```
# References
# [1] Internal: /reference_vault/<relevant-file>.md#<section>
# [2] External: <URL> - <brief description>
# [3] Standard: <RFC/ISO/etc number> - <title>
```

### Directory Structure
```
project/
├── reference_vault/          # Single source of truth
├── src/                     # Application code
│   ├── core/               # Business logic
│   ├── adapters/           # External interfaces
│   └── config/             # Configuration
├── tests/                  # Test suites
├── docs/                   # Generated documentation
├── scripts/                # Automation scripts
└── deploy/                 # Deployment configurations
```

## 6. Documentation Standards

### Inline Documentation
- Public functions: Full docstring with examples
- Private functions: Purpose and key assumptions
- Complex logic: Brief explanatory comments
- Configuration: Default values and valid ranges

### Reference Documentation
- Architecture decisions in `/reference_vault/`
- API documentation auto-generated from code
- Deployment guides with prerequisites and rollback procedures
- Troubleshooting guides with common issues and solutions

## 7. Testing Requirements

### Coverage Standards
- Minimum 80% line coverage for production code
- 100% coverage for security-critical functions
- Integration tests for all external dependencies
- Performance regression tests for critical paths

### Test Organization
- Unit tests: Fast, isolated, deterministic
- Integration tests: End-to-end workflows
- Security tests: Input validation, authorization
- Performance tests: Load, stress, memory usage

## 8. Deployment Standards

### Environment Parity
- Identical configurations across environments
- Version-pinned dependencies
- Feature flags for gradual rollouts
- Monitoring and alerting for all environments

### Rollback Capability
- Database migrations must be reversible
- Configuration changes must be rollback-safe
- Blue-green deployment for zero-downtime updates
- Automated health checks before traffic routing

## 9. Monitoring and Observability

### Logging Standards
- Structured logging (JSON format)
- Consistent log levels (ERROR, WARN, INFO, DEBUG)
- No sensitive data in logs
- Correlation IDs for request tracing

### Metrics Requirements
- Business metrics (user actions, performance)
- Technical metrics (response times, error rates)
- Infrastructure metrics (CPU, memory, disk)
- Custom dashboards for operational visibility

## 10. Security Implementation

### Authentication & Authorization
- Multi-factor authentication for administrative access
- Role-based access control with principle of least privilege
- Session management with secure tokens
- API authentication using industry standards (OAuth2, JWT)

### Data Protection
- Encryption at rest for sensitive data
- TLS 1.3 for data in transit
- Regular security audits and vulnerability assessments
- Secure coding practices and static analysis

## 11. Performance Optimization

### Resource Management
- Connection pooling for database and external services
- Caching strategies with appropriate TTL values
- Lazy loading for expensive operations
- Resource cleanup and garbage collection optimization

### Scalability
- Horizontal scaling capabilities
- Load balancing and traffic distribution
- Database optimization and query performance
- CDN usage for static content delivery

## 12. Error Handling and Recovery

### Error Classification
- User errors: Clear error messages and recovery suggestions
- System errors: Detailed logging and automatic retry mechanisms
- Critical errors: Immediate alerting and escalation procedures
- Transient errors: Exponential backoff and circuit breaker patterns

### Recovery Procedures
- Automated failover for critical services
- Data backup and restoration procedures
- Disaster recovery planning and testing
- Incident response and post-mortem processes

## 13. Code Review and Quality Assurance

### Review Criteria
- Adherence to coding standards and best practices
- Security vulnerability assessment
- Performance impact evaluation
- Documentation completeness and accuracy

### Automated Quality Gates
- Static code analysis and linting
- Automated testing suite execution
- Security scanning and dependency vulnerability checks
- Performance benchmarking and regression testing

## 14. Compliance and Audit Requirements

### Regulatory Compliance
- GDPR compliance for data privacy
- SOC 2 compliance for security controls
- Industry-specific regulations (HIPAA, PCI-DSS, etc.)
- Regular compliance audits and reporting

### Audit Trail
- All changes tracked with author, timestamp, and rationale
- Immutable audit logs for critical operations
- Regular access reviews and privilege validation
- Compliance reporting and documentation maintenance

## References
- [1] Internal: /reference_vault/PRODUCTION_GRADE_STANDARDS.md
- [2] Internal: /reference_vault/standards.md
- [3] Internal: /reference_vault/audit_trail.md
- [4] External: OWASP Secure Coding Practices
- [5] External: NIST Cybersecurity Framework