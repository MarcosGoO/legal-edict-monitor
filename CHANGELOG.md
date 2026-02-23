# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure
- Smart OCR Wrapper service with multi-engine support (Native, Tesseract, AWS Textract)
- Colombian Entity Parser for extracting Radicados, NITs, Cédulas, and names
- Database models for law firms, clients, watchlist, documents, and notifications
- REST API endpoints for document processing and client management
- Comprehensive test suite
- Pre-commit hooks configuration
- Security policy and contributing guidelines

### Changed
- Nothing yet

### Deprecated
- Nothing yet

### Removed
- Nothing yet

### Fixed
- Nothing yet

### Security
- Added .gitignore for sensitive files
- Added secrets detection in pre-commit hooks
- Added security documentation