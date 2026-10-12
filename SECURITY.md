# Security policy

This project is a development beta. Security fixes target the current beta source; older builds do not have a maintenance guarantee.

Report vulnerabilities through the repository's **Security → Report a vulnerability** option if private vulnerability reporting is enabled. Repository maintainers should enable it before publishing. Do not include API keys, customer workbooks or sensitive cell contents in public issues. If private reporting is unavailable, ask the maintainer for a private reporting channel without disclosing exploit details publicly.

AI requests send selected cells, selected context and prompts to the configured endpoint. Review proposals before applying. Environment files, backups, exports and optional logs are not encrypted. Existing macros, links and active content are preserved by workbook saves, not sanitized. The app does not execute generated code or VBA, and it does not guarantee that an existing workbook is safe to open in Excel.

CI audits dependencies against published advisories. Passing that check is not a comprehensive security assessment. See [release readiness](docs/github-release-readiness.md) for remaining verification.
