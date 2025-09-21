# Organization Standards

**Document Version:** 1.0.0  
**Last Updated:** 2024-09-21  
**Review Date:** 2024-12-21  
**Owner:** SpiralGang Development Team  
**Compliance Level:** MANDATORY - 100% Production-Grade Standards

## Overview

This document establishes the organizational framework and repository structure standards for the VARIABOT project. These standards ensure modularity, traceability, and maintainability across all project components.

## Repository Structure Standards

### Root Level Organization

```
VARIABOT/
├── README.md                    # Project overview, quick start, features
├── copilot_instructions.md      # Streamlined AI guidelines (references vault)
├── organization_instructions.md # Repository structure guide (references vault)
├── requirements.txt             # Pinned production dependencies
├── LICENSE                      # MIT license
├── .gitignore                  # Build artifacts and temporary files
├── android_rooting/             # PRIMARY: Android rooting framework
├── reference_vault/             # Single source of truth for all standards
├── .github/workflows/          # CI/CD automation and live builds
└── [AI interfaces at root]     # st-*.py, Qwen*.py for easy access
```

### Core Module Structure (`android_rooting/`)

**Primary Goal Focus**: Complete Android 13 ARM64 tablet rooting with Kali integration

```
android_rooting/
├── __init__.py                 # Module exports and version info
├── README.md                   # Module-specific documentation
├── core/                       # Core rooting logic
│   ├── __init__.py
│   ├── root_detector.py        # Multi-method root detection
│   ├── magisk_manager.py       # Magisk integration and management
│   ├── kali_integration.py     # Kali Linux chroot and NetHunter
│   ├── android_pentest.py      # Security testing framework
│   ├── privilege_escalation.py # Escalation techniques
│   └── sandbox_escape.py       # Sandbox bypass methods
├── bots/                       # Living code bots for adaptation
│   ├── __init__.py
│   ├── error_handler_bot.py    # Real-time error adaptation
│   └── kali_adapt_bot.py       # Kali-specific adaptation bot
├── utils/                      # Shared utilities
│   ├── __init__.py
│   ├── logging_system.py       # Structured logging and audit trails
│   ├── termux_compat.py        # Termux environment compatibility
│   └── package_manager.py      # Dependency management
├── scripts/                    # Executable scripts
│   ├── android_root_complete.sh # Main rooting completion script
│   ├── termux_setup.sh         # Termux environment setup
│   └── kali_chroot_setup.sh    # Kali chroot initialization
└── docs/                       # Module documentation
    ├── ANDROID_ROOTING_GUIDE.md
    ├── TERMUX_LIMITATIONS_GUIDE.md
    └── LINUX_NETWORKING_COMMANDS_CHEATSHEET.md
```

### Reference Vault Structure (`reference_vault/`)

**Immutable Standards Repository**: Single source of truth for all organizational decisions

```
reference_vault/
├── README.md                           # Vault overview and usage
├── PRODUCTION_GRADE_STANDARDS.md      # Code quality and development standards
├── ORGANIZATION_STANDARDS.md          # Repository structure (this file)
├── copilot_instructions.md            # Complete AI behavior guidelines
├── linux_kali_android.md              # Platform-specific standards
├── standards.md                        # General development standards
├── audit_trail.md                     # Change tracking and compliance
├── external_sources.md                # External reference management
├── industry_lists.md                  # Industry standards and frameworks
├── networking_cheatsheet.md           # Network security references
├── small_ai_models.md                 # AI model specifications
└── workflow_failure_analysis.md       # Failure mode documentation
```

## Naming Conventions

### File and Directory Naming

- **Directories**: `snake_case` (e.g., `android_rooting`, `reference_vault`)
- **Python Files**: `snake_case.py` (e.g., `root_detector.py`, `kali_integration.py`)
- **Shell Scripts**: `snake_case.sh` (e.g., `android_root_complete.sh`)
- **Documentation**: `UPPER_CASE.md` for standards, `Title_Case.md` for guides
- **Configuration**: `snake_case` with appropriate extensions

### Prohibited Patterns

- Spaces in any file or directory names
- Hyphens in executable script names
- Mixed case inconsistencies
- Abbreviations without context

## Module Boundaries and Dependencies

### Core Principles

1. **Clear Separation**: Each module has single responsibility
2. **Minimal Coupling**: Avoid circular dependencies
3. **Interface Contracts**: Document inputs, outputs, failure modes
4. **Environment Agnostic**: Core logic independent of deployment environment

### Dependency Management

- **Production Dependencies**: Pin exact versions in `requirements.txt`
- **Development Dependencies**: Separate `requirements_dev.txt` if needed
- **Platform Dependencies**: Document in module README files
- **Optional Dependencies**: Use feature flags and graceful degradation

## File Organization Rules

### Standard File Headers

**Python Files:**
```python
#!/usr/bin/env python3
"""
Module Description
Brief description of module purpose and capabilities

This module provides:
- Feature 1 description
- Feature 2 description  
- Feature 3 description

Compatible with: Python 3.7+, Platform specifics
"""
```

**Shell Scripts:**
```bash
#!/bin/bash
"""
Script Description
Brief description of script purpose and capabilities

This script provides:
- Functionality 1
- Functionality 2
- Error handling and recovery

Compatible with: Bash 4.0+, Termux, Standard Linux
"""

set -euo pipefail
```

### Documentation Standards

**End-of-File References Pattern:**
```
References:
- Internal: /reference_vault/PRODUCTION_GRADE_STANDARDS.md#logging
- Internal: /reference_vault/linux_kali_android.md#environment-detection  
- External: OpenTelemetry Spec — https://opentelemetry.io/docs/
```

### Version Control Integration

**Commit Message Format:**
```
type(scope): brief description

Detailed explanation of changes and rationale.

Traceability: 
- /reference_vault/ORGANIZATION_STANDARDS.md#file-organization
- /reference_vault/PRODUCTION_GRADE_STANDARDS.md#testing

Fixes #issue_number
```

## Compliance and Audit Requirements

### Change Management

1. **Vault Changes**: Require PR review and explicit approval
2. **Structure Changes**: Document migration path and rollback plan
3. **Breaking Changes**: Version bump and deprecation notice
4. **Backwards Compatibility**: Maintain for at least 2 minor versions

### Quality Gates

- All files must follow naming conventions
- Documentation must include proper vault citations
- No placeholder content in production branches
- Test coverage requirements per module type

### Audit Trail

- Track all organizational decisions in `/reference_vault/audit_trail.md`
- Document rationale for structure exceptions
- Maintain change history with responsibility assignment
- Regular compliance reviews quarterly

## Integration Points

### CI/CD Integration

- Automated structure validation in GitHub Actions
- Naming convention enforcement
- Documentation completeness checks
- Dependency security scanning

### Development Workflow Integration

- Pre-commit hooks for structure validation
- Template generation for new modules
- Automated cross-reference validation
- Documentation link checking

## References

- Internal: `/reference_vault/PRODUCTION_GRADE_STANDARDS.md` (development standards)
- Internal: `/reference_vault/copilot_instructions.md` (AI integration)  
- Internal: `/reference_vault/audit_trail.md` (change tracking)
- External: GitHub Repository Standards — https://docs.github.com/en/repositories
- External: Python Packaging Guide — https://packaging.python.org/