# AI Commerce OS - Development Conventions

## Table of Contents

1. [Code Style Guidelines](#code-style-guidelines)
2. [Git Workflow](#git-workflow)
3. [Commit Guidelines](#commit-guidelines)
4. [Testing Guidelines](#testing-guidelines)
5. [Documentation Guidelines](#documentation-guidelines)
6. [Code Review Guidelines](#code-review-guidelines)
7. [Security Guidelines](#security-guidelines)
8. [Performance Guidelines](#performance-guidelines)

## Code Style Guidelines

### TypeScript/JavaScript

#### Naming Conventions
- **Files**: `kebab-case` (e.g., `user-service.ts`, `product-list.tsx`)
- **Components**: `PascalCase` (e.g., `UserProfile`, `ProductCard`)
- **Functions/Variables**: `camelCase` (e.g., `getUserData`, `productList`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `API_BASE_URL`, `MAX_RETRIES`)
- **Types/Interfaces**: `PascalCase` (e.g., `User`, `ProductMetadata`)
- **Enums**: `PascalCase` with `UPPER_SNAKE_CASE` values

#### Code Organization
```typescript
// 1. Imports
import { ExternalDependency } from 'external-package';
import { internalDependency } from './internal';
import type { TypeImport } from './types';

// 2. Constants
const CONSTANT_VALUE = 'value';

// 3. Types/Interfaces
interface MyInterface {
  property: string;
}

// 4. Functions
function myFunction() {
  // implementation
}

// 5. Exports
export { myFunction, MyInterface };
```

#### Best Practices
- Use `const` by default, `let` only when reassignment is needed
- Use arrow functions for callbacks
- Use template literals for string interpolation
- Destructure objects and arrays when appropriate
- Use async/await for asynchronous code
- Avoid `any` type - use proper types or `unknown`
- Use strict null checks
- Prefer interfaces over type aliases for object shapes
- Use type guards for runtime type checking

### Python

#### Naming Conventions
- **Files**: `snake_case` (e.g., `user_service.py`, `product_list.py`)
- **Classes**: `PascalCase` (e.g., `UserService`, `ProductList`)
- **Functions/Variables**: `snake_case` (e.g., `get_user_data`, `product_list`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `API_BASE_URL`, `MAX_RETRIES`)
- **Private members**: `_leading_underscore` (e.g., `_internal_method`)

#### Code Organization
```python
# 1. Standard library imports
import os
from typing import Optional, List

# 2. Third-party imports
from fastapi import FastAPI
from pydantic import BaseModel

# 3. Local imports
from app.models import User
from app.services import UserService

# 4. Constants
CONSTANT_VALUE = "value"

# 5. Type definitions
class MyModel(BaseModel):
    property: str

# 6. Functions
def my_function():
    # implementation

# 7. Classes
class MyClass:
    def __init__(self):
        pass
```

#### Best Practices
- Use type hints for all function parameters and return values
- Use dataclasses for data containers
- Use Pydantic models for data validation
- Use context managers for resource management
- Follow PEP 8 style guide
- Use docstrings for all public functions and classes
- Prefer list comprehensions over map/filter
- Use f-strings for string formatting
- Avoid mutable default arguments

### SQL

#### Naming Conventions
- **Tables**: `snake_case` (e.g., `users`, `product_metadata`)
- **Columns**: `snake_case` (e.g., `created_at`, `user_id`)
- **Indexes**: `table_column_idx` (e.g., `users_email_idx`)
- **Foreign Keys**: `table_id` (e.g., `user_id`, `store_id`)

#### Best Practices
- Use consistent naming across tables
- Always include `created_at` and `updated_at` timestamps
- Use appropriate data types for columns
- Create indexes on frequently queried columns
- Use foreign keys for relationships
- Add constraints for data integrity
- Use transactions for multi-step operations

## Git Workflow

### Branch Strategy

We use a simplified Git flow:

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/***: Feature branches
- **bugfix/***: Bug fix branches
- **hotfix/***: Urgent production fixes

### Branch Naming

```
feature/trend-intelligence-service
feature/product-evaluation-algorithm
bugfix/authentication-error
hotfix/security-patch
```

### Workflow

1. Create feature branch from `develop`
2. Make commits with descriptive messages
3. Push to remote
4. Create pull request to `develop`
5. Code review and approval
6. Merge to `develop`
7. Periodically merge `develop` to `main` for releases

### Pull Request Guidelines

- **Title**: Clear and descriptive
- **Description**: Explain what and why
- **Linked Issues**: Reference related issues
- **Testing**: Describe testing performed
- **Breaking Changes**: Highlight any breaking changes
- **Reviews**: Minimum one approval required

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks
- **perf**: Performance improvements
- **ci**: CI/CD changes

### Examples

```
feat(trend-intelligence): add Google Trends API integration

Implement integration with Google Trends API to collect
trend data for market analysis.

Closes #123
```

```
fix(authentication): resolve JWT token validation error

Fix token validation that was failing on edge cases where
the token expiration was exactly at the validation time.

Fixes #456
```

### Best Practices

- Use present tense ("add" not "added")
- Use imperative mood ("add" not "adds")
- Limit subject line to 50 characters
- Wrap body at 72 characters
- Explain what and why, not how
- Reference issue numbers

## Testing Guidelines

### Unit Testing

#### TypeScript
```typescript
describe('UserService', () => {
  describe('getUser', () => {
    it('should return user when found', async () => {
      // Arrange
      const userId = '123';
      const expectedUser = { id: userId, name: 'Test' };
      
      // Act
      const user = await userService.getUser(userId);
      
      // Assert
      expect(user).toEqual(expectedUser);
    });
    
    it('should throw error when user not found', async () => {
      // Arrange
      const userId = '999';
      
      // Act & Assert
      await expect(userService.getUser(userId))
        .rejects.toThrow('User not found');
    });
  });
});
```

#### Python
```python
import pytest
from app.services import UserService

def test_get_user_found():
    # Arrange
    user_id = "123"
    expected_user = {"id": user_id, "name": "Test"}
    
    # Act
    user = UserService.get_user(user_id)
    
    # Assert
    assert user == expected_user

def test_get_user_not_found():
    # Arrange
    user_id = "999"
    
    # Act & Assert
    with pytest.raises(UserNotFoundError):
        UserService.get_user(user_id)
```

### Integration Testing

- Test service interactions
- Test database operations
- Test API endpoints
- Use test database
- Clean up after tests

### End-to-End Testing

- Test user flows
- Test critical paths
- Use realistic data
- Test across applications
- Run before releases

### Testing Best Practices

- Write tests before fixing bugs
- Aim for high coverage (>80%)
- Test edge cases and error conditions
- Use descriptive test names
- Keep tests independent
- Mock external dependencies
- Use factories for test data
- Test public interfaces, not implementation

## Documentation Guidelines

### Code Documentation

#### TypeScript
```typescript
/**
 * Retrieves a user by their ID
 * @param userId - The unique identifier of the user
 * @returns The user object or null if not found
 * @throws {UserNotFoundError} When user doesn't exist
 * @example
 * ```ts
 * const user = await getUser('123');
 * ```
 */
async function getUser(userId: string): Promise<User | null> {
  // implementation
}
```

#### Python
```python
def get_user(user_id: str) -> Optional[User]:
    """
    Retrieves a user by their ID.
    
    Args:
        user_id: The unique identifier of the user
        
    Returns:
        The user object or None if not found
        
    Raises:
        UserNotFoundError: When user doesn't exist
        
    Example:
        >>> user = get_user('123')
    """
    # implementation
```

### API Documentation

- Use OpenAPI/Swagger for API docs
- Document all endpoints
- Include request/response examples
- Document error responses
- Keep documentation in sync with code

### README Files

Each package should have a README with:
- Purpose and description
- Installation instructions
- Usage examples
- API documentation
- Testing instructions
- Contributing guidelines

### Architecture Documentation

- Document architectural decisions
- Use diagrams for complex systems
- Keep documentation up to date
- Use ARCHITECTURE.md for system design
- Document trade-offs and alternatives

## Code Review Guidelines

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Code is well-documented
- [ ] Tests are included and passing
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed
- [ ] Error handling is appropriate
- [ ] No unnecessary complexity
- [ ] Dependencies are justified
- [ ] Breaking changes are documented

### Review Process

1. Automated checks pass (lint, tests)
2. Reviewer examines code changes
3. Reviewer provides constructive feedback
4. Author addresses feedback
5. Reviewer approves changes
6. Changes are merged

### Review Best Practices

- Be respectful and constructive
- Explain the "why" for suggestions
- Focus on the code, not the person
- Respond to reviews promptly
- Keep reviews focused and actionable
- Use inline comments for specific issues

## Security Guidelines

### Authentication & Authorization

- Use JWT for API authentication
- Implement role-based access control
- Never store plain text passwords
- Use secure token storage
- Implement token expiration
- Use HTTPS in production

### Data Protection

- Encrypt sensitive data at rest
- Use TLS for data in transit
- Validate all user input
- Sanitize data before storage
- Implement proper error handling
- Never log sensitive information

### Dependencies

- Keep dependencies updated
- Use dependency scanning tools
- Review security advisories
- Use lock files for reproducibility
- Audit third-party code
- Prefer well-maintained packages

### Secrets Management

- Never commit secrets to repository
- Use environment variables for secrets
- Rotate secrets regularly
- Use secret management services in production
- Limit secret access to necessary services
- Audit secret usage

## Performance Guidelines

### Database

- Use indexes on frequently queried columns
- Avoid N+1 queries
- Use connection pooling
- Implement query caching
- Optimize joins and subqueries
- Use pagination for large result sets
- Monitor query performance

### API

- Implement rate limiting
- Use compression for responses
- Cache frequently accessed data
- Use async operations for I/O
- Implement pagination
- Optimize response sizes
- Monitor API performance

### Frontend

- Use code splitting
- Implement lazy loading
- Optimize images and assets
- Use CDN for static assets
- Implement caching strategies
- Minimize bundle sizes
- Monitor Core Web Vitals

### Caching Strategy

- Cache frequently accessed data
- Use appropriate cache expiration
- Implement cache invalidation
- Use multiple cache layers
- Monitor cache hit rates
- Cache computationally expensive operations

---

## Additional Resources

- [TypeScript Style Guide](https://typescript.style/)
- [Python PEP 8](https://peps.python.org/pep-0008/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Testing Best Practices](https://testingjavascript.com/)
- [OWASP Security Guidelines](https://owasp.org/)

---

**Document Version**: 1.0  
**Last Updated**: 2026-08-01  
**Maintained By**: Development Team
