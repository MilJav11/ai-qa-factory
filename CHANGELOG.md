# Changelog

All notable changes to this project are documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.1] - 2026-08-14

### Added

- Configured active Playwright test discovery through `testDir: './tests'`.
- Added a SauceDemo checkout test scenario.
- Added agent working rules and offline tests for Guardian safety, DOM sanitization, and AI provider error handling.

### Changed

- Clarified project documentation and metadata around the human-in-the-loop self-healing workflow.
- Kept active tests in `tests/` and preserved historical prototypes as archive-only code.
- Protected active files from cleanup behavior.

### Security

- Stopped tracking runtime DOM dumps and error logs; Guardian queue and test-report artifacts remain uncommitted.
- Restricted Guardian repair targets to existing `tests/**/*.spec.ts` files.
- Sanitized and size-bounded DOM content before external AI submission.
- Validated AI response schema and AI-suggested locator expressions before applying a repair.
- Applied approved repair writes atomically.

### Fixed

- Handled AI provider and invalid-response errors without exposing unsafe details.
- Added path restrictions for Guardian test targets.

## [1.0.0]

- Original project prototype.
