# Contributing to Kyiv Alert Monitor System

Thank you for your interest in contributing to the Kyiv Alert Monitor System! This document provides guidelines and information for contributors.

## Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors.

## How to Contribute

### Reporting Bugs

1. Check the [Issues](https://github.com/Samoilenko-Alex/Alert_System/issues) page to see if the bug has already been reported
2. If not, create a new issue with:
   - Clear title describing the bug
   - Detailed description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, etc.)

### Suggesting Features

1. Check existing issues for similar suggestions
2. Create a new issue with:
   - Clear title for the feature
   - Detailed description of the proposed feature
   - Use case or problem it solves
   - Any implementation ideas

### Contributing Code

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Add tests if applicable
5. Ensure all tests pass: `python test_system.py`
6. Commit your changes: `git commit -m 'Add some feature'`
7. Push to your branch: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/Samoilenko-Alex/Alert_System.git
cd Alert_System

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

## Coding Standards

### Code Quality Tools

This project uses automated code quality tools:

- **Black**: Code formatting
- **Flake8**: Linting and style checking
- **Pre-commit**: Automated checks before commits

Run quality checks:
```bash
pre-commit run --all-files
```

### Python Style Guidelines

- Follow PEP 8 style guidelines
- Maximum line length: 127 characters
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Use type hints where appropriate

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb in imperative mood (e.g., "Add", "Fix", "Update")
- Keep the first line under 50 characters
- Reference issue numbers when applicable

Example:
```
Fix audio playback synchronization

- Resolve timing issues in player service
- Add proper event handling for audio events
- Update tests for synchronization logic

Closes #123
```

### Testing

- Write tests for new features and bug fixes
- Ensure all existing tests pass before submitting PR
- Test edge cases and error conditions
- Use descriptive test names and assertions

Run tests:
```bash
python test_system.py
```

## Pull Request Process

1. Ensure your PR addresses a specific issue or implements a requested feature
2. Update documentation (README, CHANGELOG) if needed
3. Add or update tests for new functionality
4. Ensure all CI checks pass (GitHub Actions)
5. Request review from maintainers
6. Address any review feedback
7. Squash commits if requested before merge

## Documentation

- Update README.md for significant user-facing changes
- Add docstrings to new functions and classes
- Update CHANGELOG.md for all user-facing changes
- Keep inline comments clear and helpful
- Update issue/PR templates if needed

## CI/CD

The project uses GitHub Actions for continuous integration:

- **Automated Testing**: Runs on every push and PR
- **Code Quality**: Black formatting and Flake8 linting
- **Multi-platform**: Tests on Windows, Linux, and macOS

Ensure your changes don't break the CI pipeline.

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_system.py
```

## Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions small and focused
- Use type hints where appropriate

## Testing

- Add unit tests for new features
- Ensure existing tests still pass
- Test on multiple Python versions if possible
- Test edge cases and error conditions

## Commit Messages

Use clear, descriptive commit messages:
- `feat: add new alert simulation feature`
- `fix: resolve audio playback issue on Windows`
- `docs: update installation instructions`
- `refactor: simplify alert monitoring logic`

## Pull Request Process

1. Ensure your PR description clearly describes the changes
2. Reference any related issues
3. Ensure CI checks pass
4. Wait for review and address any feedback
5. Once approved, your PR will be merged

## Areas for Contribution

- **Bug fixes**: Help improve system stability
- **Documentation**: Improve README, add examples
- **Testing**: Add more comprehensive tests
- **Features**: New functionality for alert management
- **Performance**: Optimize API calls and audio playback
- **UI/UX**: Improve web interface

## Questions?

If you have questions about contributing, feel free to:
- Open an issue with your question
- Contact the maintainers

Thank you for helping make the Kyiv Alert Monitor System better! 🇺🇦