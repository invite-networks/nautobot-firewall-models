# Release Checklist

This repository is maintained by INVITE Networks and is not published to PyPI. Releases are git tags on `main` with a matching GitHub release. Versions follow [Semantic Versioning](https://semver.org/).

## Refresh Dependencies

Every minor version release should refresh `uv.lock` so that it lists the most recent stable release of each package:

1. Run `uv lock --upgrade` to update all packages, or `uv lock --upgrade-package <package>` to update one.
2. Run `uv sync` to install the refreshed versions.
3. Rebuild the development environment with `uv run invoke build` and run all tests with `uv run invoke tests`. Check that the UI and API function as expected.

## Check the Documentation

Make sure any new or changed features are covered in the documentation. Start the documentation server with `uv run mkdocs serve` to preview your changes as you make them.

## Bump the Version

Use `uv version` to show or change the version in `pyproject.toml`:

```shell
uv version --bump patch   # 3.0.1 -> 3.0.2
uv version --bump minor   # 3.0.1 -> 3.1.0
uv version --bump major   # 3.0.1 -> 4.0.0
```

## Generate the Release Notes

Release notes are built with [Towncrier](https://towncrier.readthedocs.io/) from the fragments in the `changes/` directory:

```shell
uv run invoke generate-release-notes
```

For a new major or minor version, this creates `docs/admin/release_notes/version_{major}.{minor}.md`. Fill in its `Release Overview` section with a short summary of the most notable changes.

## Tag and Publish

1. Commit the version bump and release notes to `main`.
2. Tag the release and push it: `git tag v3.0.2 && git push origin main v3.0.2`.
3. Create a GitHub release from the tag using the generated release notes.
