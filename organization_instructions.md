# Organization Instructions

## Repository Structure

This document outlines the VARIABOT repository organization and contribution workflow to ensure modularity, traceability, and seamless integration per Copilot principles.

**For detailed organizational standards, see:** `/reference_vault/ORGANIZATION_STANDARDS.md`

## Directory Structure

```
VARIABOT/
├── README.md                    # Project overview and quick start
├── copilot_instructions.md      # AI behavior guidelines (this references vault)
├── organization_instructions.md # Repository structure (this file)
├── requirements.txt             # Pinned dependencies
├── android_rooting/             # Primary goal: Android rooting framework
│   ├── core/                   # Root detection, Magisk handlers
│   ├── bots/                   # Living code bots for error adaptation
│   ├── utils/                  # Shared utilities
│   ├── scripts/                # Executable scripts
│   └── docs/                   # Guides and documentation
├── reference_vault/             # Single source of truth for all standards
│   ├── PRODUCTION_GRADE_STANDARDS.md
│   ├── copilot_instructions.md  # Complete AI guidelines
│   ├── linux_kali_android.md   # Platform-specific standards
│   └── ORGANIZATION_STANDARDS.md
├── st-*.py                     # Streamlit AI chatbot interfaces
├── Qwen110BChat.py             # Terminal AI interface
└── .github/workflows/          # CI/CD automation
```

## Naming Conventions

- **Folders**: snake_case (e.g., `android_rooting`)
- **Files**: snake_case for scripts (e.g., `finalize_root.sh`)
- **Modules**: Domain-aligned (e.g., `root_detector.py`)
- **No spaces or hyphens in executable names**

## Contribution Workflow

1. **Fork and Branch**: Create feature branch from main
2. **Integration First**: Extend existing modular units, remove unrelated code
3. **Standards Compliance**: Follow `/reference_vault/` guidelines
4. **Testing**: Add tests alongside new logic  
5. **PR Requirements**: Include purpose, scope, traceability, rollback plan

## Core Principles

- **Modularity**: Clear boundaries, avoid cyclic dependencies
- **Traceability**: All decisions trace back to `/reference_vault/`
- **No Duplication**: Cite vault sections instead of restating
- **Merge-Ready**: No placeholder text, no speculative TODOs

## File Organization Rules

- **Primary Focus**: Android rooting in `/android_rooting/`
- **Extensions**: AI chatbots and optional features at root level
- **Standards**: All foundational rules in `/reference_vault/`
- **Documentation**: Inline citations to vault, external refs at end

## Gap Handling

When requirements exceed existing vault coverage:
1. Implement minimal necessary logic
2. Insert `// GAP:` comment  
3. Recommend vault addition in PR
4. Surface in PR traceability section

## References

- Internal: `/reference_vault/ORGANIZATION_STANDARDS.md` (detailed structure)
- Internal: `/reference_vault/PRODUCTION_GRADE_STANDARDS.md` (quality standards)
- Internal: `/reference_vault/copilot_instructions.md` (AI guidelines)