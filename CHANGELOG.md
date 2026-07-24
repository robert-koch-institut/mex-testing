# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- moved http-test-server from mex-backend, with shorter url path and `MEX_TESTING_` envs

### Changes

- new template https://github.com/robert-koch-institut/mex-template/releases/tag/1.3.0
- updated template to https://github.com/robert-koch-institut/mex-template/commit/944944
- HEAD requests now return 404 when the corresponding GET would return 404
- container wiring (Dockerfile, compose, Makefile) uses `MEX_TESTING_HTTP_SERVER_*`
  envs, port 8080 and the `/v0/_system/check` health path
- use `httpx2` for the test client instead of the deprecated `httpx` integration

### Deprecated

### Removed

### Fixed

### Security

- http test server rejects path-traversal requests that escape the data directory
