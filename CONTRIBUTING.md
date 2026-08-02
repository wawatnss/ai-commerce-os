# Contributing to AI Commerce OS

Thank you for your interest in contributing to AI Commerce OS! This document provides guidelines and instructions for contributing to the project.

## Project Priority Rule (since Phase 8)

Every new phase or feature must move at least one measurable metric:

- **Conversion** (does it help a visitor become a customer?)
- **SEO** (does it improve discoverability/ranking?)
- **Speed** (does it make the store faster?)
- **User experience** (does it make the store easier/more pleasant to use?)
- **Credibility/trust** (does it make the store more trustworthy?)

If a proposed feature doesn't move any of these, it is not a priority - purely
technical/infrastructure modules are no longer accepted without a direct,
explainable impact on one of the metrics above. See
[PHASE8_REPORT.md](./PHASE8_REPORT.md) for the first feature built under this
rule (the Conversion Optimization Engine).

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Workflow](#development-workflow)
3. [Coding Standards](#coding-standards)
4. [Testing](#testing)
5. [Submitting Changes](#submitting-changes)
6. [Reporting Issues](#reporting-issues)
7. [Community Guidelines](#community-guidelines)

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Read the [ARCHITECTURE.md](./ARCHITECTURE.md)
- Read the [DEVELOPMENT_CONVENTIONS.md](./docs/DEVELOPMENT_CONVENTIONS.md)
- Set up your development environment (see [INSTALL.md](./INSTALL.md))
- Familiarized yourself with the project structure

### Setting Up Your Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/ai-commerce-os.git
   cd ai-commerce-os
   ```
3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/original-repo/ai-commerce-os.git
   ```
4. Install dependencies:
   ```bash
   npm install
   cd apps/api
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
5. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

## Development Workflow

### Branch Strategy

- Create a new branch for your work:
  ```bash
  git checkout -b feature/your-feature-name
  # or
  git checkout -b bugfix/your-bug-fix
  ```

### Making Changes

1. Make your changes following the coding standards
2. Write tests for your changes
3. Update documentation if needed
4. Commit your changes with clear messages

### Keeping Your Branch Updated

```bash
git fetch upstream
git rebase upstream/develop
```

### Running Tests

```bash
# Run all tests
npm test

# Run tests for specific package
cd packages/database
npm test

# Run Python tests
cd apps/api
pytest
```

### Code Quality

```bash
# Run linting
npm run lint

# Run type checking
npm run typecheck

# Format code
npm run format
```

## Coding Standards

### General Guidelines

- Follow the [DEVELOPMENT_CONVENTIONS.md](./docs/DEVELOPMENT_CONVENTIONS.md)
- Write clean, readable code
- Add comments for complex logic
- Use meaningful variable and function names
- Keep functions small and focused
- DRY (Don't Repeat Yourself)

### TypeScript

- Use strict TypeScript configuration
- Avoid `any` type
- Use proper type definitions
- Follow naming conventions
- Use interfaces for object shapes

### Python

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for public functions
- Use Pydantic for data validation
- Follow naming conventions

### Testing

- Write unit tests for new features
- Aim for high test coverage
- Test edge cases
- Use descriptive test names
- Mock external dependencies

## Testing

### Test Requirements

- All new features must include tests
- Bug fixes should include regression tests
- Tests must pass before submission
- Maintain test coverage above 80%

### Running Tests

```bash
# TypeScript/JavaScript tests
npm test

# Python tests
cd apps/api
pytest

# End-to-end tests
npm run test:e2e
```

### Writing Tests

See [DEVELOPMENT_CONVENTIONS.md](./docs/DEVELOPMENT_CONVENTIONS.md#testing-guidelines) for detailed testing guidelines.

## Submitting Changes

### Pull Request Process

1. Update your branch with the latest changes:
   ```bash
   git fetch upstream
   git rebase upstream/develop
   ```

2. Push your changes:
   ```bash
   git push origin feature/your-feature-name
   ```

3. Create a pull request on GitHub

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] Commit messages follow guidelines
- [ ] No merge conflicts
- [ ] PR description is clear and descriptive
- [ ] Linked to relevant issues

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included
- [ ] Documentation updated
- [ ] No merge conflicts

## Related Issues
Closes #123
```

### Review Process

1. Automated checks must pass
2. At least one approval required
3. Address review feedback
4. Maintain commit history cleanliness

## Reporting Issues

### Bug Reports

When reporting bugs, include:

- Clear description of the problem
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, versions)
- Screenshots if applicable
- Error messages/stack traces

### Feature Requests

When requesting features, include:

- Clear description of the feature
- Use case and motivation
- Proposed implementation (if known)
- Alternative approaches considered
- Potential impact on existing features

### Issue Template

```markdown
## Type
- [ ] Bug
- [ ] Feature Request
- [ ] Question

## Description
Clear description of the issue or request

## Steps to Reproduce (for bugs)
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS:
- Version:
- Browser (if applicable):

## Additional Context
Any other relevant information
```

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Accept feedback gracefully
- Collaborate and communicate openly

### Communication

- Use GitHub for discussions
- Be clear and concise in communications
- Ask questions when unsure
- Share knowledge with the community
- Document decisions and discussions

### Recognition

- Credit contributors for their work
- Thank reviewers for their time
- Celebrate milestones and achievements
- Recognize helpful community members

## Getting Help

- Check existing documentation
- Search existing issues
- Ask questions in GitHub Discussions
- Contact maintainers for critical issues

## License

By contributing, you agree that your contributions will be licensed under the project's license.

---

**Document Version**: 1.0  
**Last Updated**: 2026-08-01  
**Maintained By**: Development Team
