# Contributing to cp-font-gen

Thank you for your interest in contributing to cp-font-gen!

## Getting Started

For detailed development instructions, see **[docs/development.md](docs/development.md)**.

To quickly get up to speed, see **[docs/quick-start.md](docs/quick-start.md)**.

## How to Contribute

### Reporting Bugs

- [Open an issue](../../issues) with:
  - Your config file
  - Debug output: `cp-font-gen generate --config config.yaml --debug`
  - Expected vs actual behavior
  - System info (OS, Python version, tool versions)

### Requesting Features

- [Open an issue](../../issues) describing:
  - The use case and problem it solves
  - Example of how it might work
  - Why it would benefit other users

### Submitting Pull Requests

**Before starting:**

1. [Open an issue](../../issues) to discuss major changes
2. Check if someone else is working on it
3. Fork the repository

**Development process:**

1. See **[docs/development.md](docs/development.md)** for:
   - Development environment setup
   - Running tests
   - Code style guidelines
   - Project structure
   - Adding features

2. Make your changes:
   - Write tests for new functionality
   - Update documentation as needed
   - Follow existing code style

3. Test thoroughly:

   ```bash
   uv run pytest
   cp-font-gen generate --config examples/minimal/config.yaml
   ```

4. Submit PR with clear description

**PR Checklist:**

- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated (if applicable)
- [ ] Examples added/updated (if applicable)
- [ ] Code follows project style
- [ ] Commit messages are clear

## Documentation

### What to Update

- **User-facing changes** → Update README.md and docs/user-guide.md
- **New config options** → Update docs/configuration.md and examples
- **New commands** → Update README.md and docs/user-guide.md
- **Bug fixes** → Update docs/troubleshooting.md (if relevant)
- **Internal changes** → Update docs/architecture.md

See **[docs/development.md](docs/development.md)** for documentation style guidelines.

## Development Resources

- **[docs/development.md](docs/development.md)** - Complete development guide
- **[docs/architecture.md](docs/architecture.md)** - Design decisions and internals
- **[Issue Tracker](../../issues)** - Report bugs or request features
- **[Examples](examples/)** - Working example configurations

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn
- Assume good intentions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Questions?** See [docs/development.md](docs/development.md) or [open an issue](../../issues).
