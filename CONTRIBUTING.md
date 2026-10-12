# Contributing

Use Python 3.13 or 3.14 with Tkinter and a desktop display.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install . -r requirements-test.txt
python -m unittest discover -s tests -v
```

For headless Linux, install Tkinter, xvfb and xauth, then run desktop checks under `xvfb-run -a`. Provider tests use mocks and generated non-sensitive workbooks; do not commit credentials or customer files. Add regression coverage for safety or persistence fixes. Review the workbook support contract when changing file persistence.

For an installed-package check, build a wheel, install it, change to a directory outside the checkout and run `python -I -m app --check-install` and the tests using the absolute tests path. CI does this on Windows/Linux Python 3.13/3.14.

Use the pip setup above. The historical `uv.lock` has not been regenerated or validated for the current Python matrix.

Release preparation is described in [GitHub release readiness](docs/github-release-readiness.md). The release workflow produces a draft prerelease; a maintainer reviews the evidence before publishing it.
