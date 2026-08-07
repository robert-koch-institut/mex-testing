# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- added mssql test server with seeding for kvis, ifsg and grippeweb

### Changes

- new template https://github.com/robert-koch-institut/mex-template/releases/tag/1.5.0
### Deprecated

### Removed

- BREAKING: remove support for python 3.11, 3.12, and 3.13

### Fixed

### Security

## [0.1.1] - 2026-07-31

### Fixed

- set default port in settings to 8050 as per dockerfile

## [0.1.0] - 2026-07-30

### Added

- moved http-test-server from mex-backend, with shorter url path and `MEX_TESTING_` envs
- test data from mex-extractors

### Changes

- new template https://github.com/robert-koch-institut/mex-template/releases/tag/1.3.0
- updated template to https://github.com/robert-koch-institut/mex-template/commit/944944

### Security
