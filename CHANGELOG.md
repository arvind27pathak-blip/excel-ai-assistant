# Changelog

## 1.0.0b1

First prepared beta release of the supervised spreadsheet text transformation workflow.

- Review, select, apply and discard AI proposals before saving; retain partial results on cancellation.
- Confirm the selected provider, cells and context before sending data.
- Add OpenRouter provider selection, a separate session-only key, editable model IDs, connection testing and `OPENROUTER_API_KEY` support.
- Preserve unrelated Excel package parts during cell edits; add worksheet selection and guards for unsafe edits.
- Preserve text identifiers; save formula-looking AI text as text; neutralize CSV formula prefixes.
- Detect external source changes, write atomically, keep rotating backups and provide snapshot recovery.
- Keep API keys out of saved preferences and logging opt-in, including after resetting preferences.
- Fix carriage-return preservation and invalid usage-estimate settings.
- Add wheel installation, diagnostics, representative workbook fixtures and installed-package checks.
- Add GitHub draft beta release automation, artifact checksums and dependency audit gates.

Known release limitations are documented in [release notes](docs/releases/1.0.0b1.md) and [the compatibility report](docs/workbook-compatibility.md).
