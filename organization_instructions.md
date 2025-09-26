
# Organization Instructions

This document outlines the repository structure, file organization, and contribution workflow to ensure modularity, traceability, and seamless integration per Copilot principles. All organization traces to /reference_vault/ORGANIZATION_STANDARDS.md (GAP: propose addition for detailed folder schemas).

## Repository Structure
- **Root Level**:
  - `README.md`: Overview, quick start, usage examples.
  - `copilot_instructions.md`: AI behavior guidelines.
  - `organization_instructions.md`: This file.
  - `requirements.txt`: Pinned dependencies.
  - `LICENSE`: MIT license.
- **android_rooting/** (Primary Goal Focus): Core for tablet root finalization.
  - `core/`: Root detection, Magisk handlers (e.g., `magisk_integration.py`).
  - `bots/`: Living code bots for error adaptation (e.g., `kali_adapt_bot.py`—Kali chroot monitors).
  - `utils/`: Shared utilities (e.g., `env_detect.sh`).
  - `scripts/`: Executables (e.g., `finalize_root.sh`, `termux_kali_chroot.sh`).
  - `docs/`: Guides (e.g., `rooting_guide.md`).
- **/extensions/**: Segregated non-core (e.g., AI chatbots: `Qwen110BChat.py`, `st-*.py`). Download/integrate optionally via feature flags.
- **/reference_vault/**: Single source of truth (standards files below).
- **.github/workflows/**: GitHub Actions for live terminal builds (e.g., `root_bot.yml` for Kali adaptation).

## Naming Conventions
- Folders: kebab-case (e.g., android-rooting).
- Files: snake_case (e.g., finalize_root.sh); no spaces/hyphens in scripts.
- Modules: Domain-aligned (e.g., root_adaptor.py).

## Contribution Workflow
1. Fork and create feature branch (e.g., `feat/kali-bots`).
2. Integrate existing units; remove unrelated code.
3. Add tests/migrations; run pre-commit hooks (set -euo pipefail).
4. Submit PR per checklist in copilot_instructions.md.
5. For extensions: Isolate in /extensions/; optional seamless import via `importlib`.

## Gap Handling
Mark with // GAP: and PR traceability.

References:
- Internal: /reference_vault/ORGANIZATION_STANDARDS.md#structure
- External: GitHub Docs — https://docs.github.com/en/actions
