# GitHub release readiness — 2026-10-11

## Decision

Prepared for a **draft beta prerelease, `v1.0.0b1`**, subject to successful GitHub checks and the manual validation below. A stable production release is not justified by local evidence. Nothing was pushed or published: this workspace has no `.git` directory or configured remote, so remote repository settings and Actions results could not be inspected.

## Findings fixed in this review

| Finding | Fix |
| --- | --- |
| Stable version and UI labels disagreed with beta status | Package, application and historical lock metadata now use `1.0.0b1`; About reads the application version. |
| Update menu claimed the latest version without checking a server | It reports the installed version and states that automatic update checking is unavailable. |
| Resetting preferences or normalizing malformed logging settings enabled disk logging | Logging stays opt-in after either operation. Removed logger handlers are closed. |
| XML newline normalization changed generated carriage returns | Carriage returns are written as character references; the regression checks exact text round-trip. |
| Invalid token settings crashed the usage estimator | Shared settings validation displays an error and stops estimation. |
| No GitHub release pipeline or artifact inventory | Added gated wheel/source builds, source rebuild check, installed-package matrix, runtime advisory audit, checksums and draft-only prerelease creation. |
| Source archives could miss the representative fixture helper and useful release files | Explicit manifest includes tests, fixture generation, release checker, license and documentation. Distribution checks reject missing modules, wrong metadata and common private/generated files. |

## Local evidence

- **74 tests passed** against the source and the installed beta wheel, including real Tk desktop flows, workbook preservation, save failures, review control and release guards.
- Both installed launchers create a real Tk root outside the checkout. `pip check` reports no broken requirements.
- Wheel and source archive build using the declared setuptools backend. Version/tag, MIT metadata, launcher and required-file checks pass; SHA256SUMS and a JSON inventory are generated. Common private/generated files and API credential patterns are checked; this is not a comprehensive secret or security audit.
- Source archive contains the complete test suite and representative fixture helper; its wheel can be rebuilt independently. Application modules are compared between original and rebuilt wheels.
- Workflow YAML parses locally; the release dependency graph and draft/prerelease flags are checked. GitHub Actions has not executed here.

Local execution is Windows/Python 3.14 with cached dependency wheels and a workspace temporary-directory adapter required by this managed environment. This is not evidence of a clean operating-system or network installation. See [workbook compatibility](workbook-compatibility.md) for the workbook corpus and runtime boundaries.

## Gates before publication

1. Commit this source in the intended GitHub repository and run the checks. Confirm all four Windows/Linux × Python 3.13/3.14 jobs and the advisory audit pass. Audit failures or unavailable advisory data must be resolved before publication. Advisory scanning could not run locally because the tool and advisory service are unavailable in this offline environment.
2. Run a small live-provider smoke test for each advertised provider/model, covering success, authentication failure, incomplete output and cancellation. Local provider tests are mocked.
3. Open representative edited workbooks in Microsoft Excel. Use genuine macro/pivot/slicer/connection examples before claiming runtime support for those features; current advanced opaque/VBA fixtures test package preservation only.
4. Enable private vulnerability reporting and review repository access and tag protection. Avoid including API keys or customer data in source or assets.
5. Review the draft body and artifacts, add the successful Actions run link, and keep the **prerelease** label. macOS, signed installers, large-file performance and the historical uv lock remain outside current verified scope.

The unresolved live-provider and real-Excel checks prevent a production-readiness claim. A maintainer may publish a clearly limited beta after the automated gates pass and the limitations are accepted explicitly in the release notes.

## Release procedure

```powershell
python -m pip install . -r requirements-test.txt build
python -m unittest discover -s tests -v
python -m build
python scripts/check_release.py --tag v1.0.0b1 --dist dist
```

Use a fresh `dist` directory: the checker requires exactly one wheel and one source archive. Commit the reviewed changes, create and push the matching tag in your intended repository:

```powershell
git tag -a v1.0.0b1 -m "Excel AI Assistant 1.0.0b1 beta"
git push origin v1.0.0b1
```

These are maintainer instructions, not actions performed in this review. The release workflow validates the beta tag, builds and checks both distributions, rebuilds the source archive, tests the exact wheel through reusable CI, audits runtime requirements and creates a draft prerelease. It does not publish the draft or upload to PyPI. Manual dispatch must select the existing version tag, not a branch. A rerun fails if a release already exists instead of replacing assets silently.

GitHub's [reusable workflow documentation](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows) describes the shared check workflow; the [GitHub CLI release reference](https://cli.github.com/manual/gh_release_create) documents draft, prerelease and tag-verification options. Python's [packaging flow](https://packaging.python.org/en/latest/flow/) describes the wheel/source distribution split. [pip-audit](https://github.com/pypa/pip-audit) checks requirements and their transitive dependencies against published advisories.
