# Changelog

All notable changes to the Kyiv Alert Monitor System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions CI/CD pipeline
- Pre-commit hooks for code quality
- Issue and PR templates
- Comprehensive .gitignore
- Development documentation

### Changed
- Improved project structure
- Enhanced README with development guidelines
- Cleaned up code comments and logging

### Fixed
- Repository structure cleanup
- Removed empty directories
- Updated dependencies

## [2.0.0] - 2026-05-05

### Added
- Initial public release of Kyiv Alert Monitor System
- Real-time air raid alert monitoring via UkraineAlarm API
- Automated minute of silence scheduling at 09:00 daily
- Web-based control panel for system management
- Audio playback system with priority handling
- Comprehensive logging and alert history
- Testing and simulation tools
- Multi-PC operation support
- Flag-based event management system

### Features
- One-time siren playback (non-looping)
- All-clear signal notifications
- Emergency stop functionality
- Real-time log viewing
- Command-line simulation tools
- Full system testing suite

### Technical
- Flask web server integration
- Python virtual environment support
- Windows batch file automation
- File-based flag mechanism for event coordination
- Double-launch protection for audio service

## [1.0.0] - 2026-04-01

### Added
- Basic alert monitoring functionality
- Initial audio playback system
- Web interface prototype
- Core monitoring and player services

### Changed
- Improved event priority handling
- Enhanced logging system

---

## Types of changes
- `Added` for new features
- `Changed` for changes in existing functionality
- `Deprecated` for soon-to-be removed features
- `Removed` for now removed features
- `Fixed` for any bug fixes
- `Security` in case of vulnerabilities