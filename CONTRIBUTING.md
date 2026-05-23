# Contributing to Intelligent Log Analyzer

Thank you for your interest in contributing to the Intelligent Log Analyzer project! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome all contributors regardless of background
- Provide constructive feedback
- Focus on code quality and improvements

## Getting Started

### Prerequisites
- Python 3.11+
- Git
- Docker (optional)
- PostgreSQL (for development with real database)

### Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd log-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
make dev

# Initialize database
make db-init

# Run development server
make run
```

## Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
# or for bug fixes
git checkout -b fix/your-bug-fix
```

### 2. Make Changes
- Write clean, readable code
- Add docstrings to functions
- Include type hints
- Add comments for complex logic

### 3. Testing
```bash
# Run all tests
make test

# Run specific test
pytest tests/test_parser.py -v

# Run with coverage
make coverage
```

### 4. Code Quality
```bash
# Format code
make format

# Lint code
make lint

# Type checking
make type-check

# All checks
make quality
```

### 5. Commit Changes
```bash
# Commit with descriptive message
git commit -m "feat: add new error categorization

- Added database error category detection
- Improved severity calculation
- Added test cases"
```

### 6. Push and Create PR
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with a clear description.

## Commit Message Guidelines

Use conventional commits format:

```
type(scope): subject

body

footer
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test additions or changes
- `ci`: CI/CD changes
- `chore`: Dependency updates, etc.

### Examples
```
feat(parser): add support for JSON log format

- Implemented JSON log parser
- Added regex pattern for JSON detection
- Updated tests for JSON format

Closes #123
```

```
fix(api): handle file upload timeout gracefully

- Added timeout exception handling
- Return proper error response
- Log timeout events for debugging
```

## Code Style Guide

### Python Style
- Follow PEP 8
- Use Black for formatting (`max-line-length=100`)
- Use type hints for all functions
- Document with docstrings (Google style)

### Example
```python
def calculate_health_score(
    error_count: int,
    warning_count: int,
    info_count: int
) -> float:
    """
    Calculate system health score based on log composition.

    Args:
        error_count: Number of error level logs
        warning_count: Number of warning level logs
        info_count: Number of info level logs

    Returns:
        Health score as percentage (0-100)

    Raises:
        ValueError: If counts are negative

    Example:
        >>> calculate_health_score(10, 20, 70)
        75.0
    """
    if error_count < 0 or warning_count < 0 or info_count < 0:
        raise ValueError("Log counts cannot be negative")

    total = error_count + warning_count + info_count
    if total == 0:
        return 100.0

    score = (info_count / total) * 100
    score -= (error_count / total) * 30
    score -= (warning_count / total) * 10

    return max(0, min(100, score))
```

### Imports
- Group imports: standard library, third-party, local
- Use `isort` for automatic sorting
- Avoid `import *`

```python
import logging
from datetime import datetime
from typing import Optional, List

import sqlalchemy
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from config import settings
from models.database import LogEntry
```

## Database Changes

### Adding a New Model
1. Create model in `models/database.py`
2. Add Pydantic schema in `schemas.py`
3. Create migration (future: Alembic)
4. Update API endpoints if needed
5. Add tests

### Example
```python
# In models/database.py
class NewModel(Base):
    __tablename__ = "new_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# In schemas.py
class NewModelResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True
```

## API Changes

### Adding New Endpoint
1. Add route in `routes/logs.py`
2. Add Pydantic schemas in `schemas.py`
3. Document with docstrings
4. Add tests in `tests/`
5. Update API documentation

### Example
```python
@router.get("/new-endpoint")
def get_new_data(db: Session = Depends(get_db)):
    """
    Get new data.

    Returns:
        Data with detailed information
    """
    # Implementation
    return {"data": []}
```

## Testing Guidelines

### Test Structure
```
tests/
├── __init__.py
├── test_parser.py
├── test_api.py
├── test_database.py
└── test_exceptions.py
```

### Writing Tests
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestLogUpload:
    """Tests for log upload endpoint"""

    def test_upload_valid_file(self):
        """Test uploading a valid log file"""
        with open("sample_logs/sample.log", "rb") as f:
            response = client.post(
                "/api/v1/logs/upload",
                files={"file": f}
            )

        assert response.status_code == 201
        assert response.json()["health_score"] >= 0

    def test_upload_invalid_file_type(self):
        """Test uploading invalid file type"""
        response = client.post(
            "/api/v1/logs/upload",
            files={"file": ("test.txt", b"invalid")}
        )

        assert response.status_code == 400

    def test_upload_file_too_large(self):
        """Test uploading oversized file"""
        large_content = b"x" * (51 * 1024 * 1024)
        response = client.post(
            "/api/v1/logs/upload",
            files={"file": ("large.log", large_content)}
        )

        assert response.status_code == 413
```

### Test Coverage
- Aim for >80% coverage
- Test happy path
- Test error cases
- Test edge cases

## Documentation

### Update Documentation For
- New features
- API changes
- Configuration options
- Deployment instructions
- Troubleshooting tips

### Document In
- Docstrings (code documentation)
- README.md (general information)
- DEPLOYMENT.md (deployment guide)
- API endpoints (Swagger/OpenAPI)

## Pull Request Process

1. **Before submitting:**
   - Ensure all tests pass: `make test`
   - Run quality checks: `make quality`
   - Update documentation
   - Add changelog entry

2. **PR Description:**
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   How was this tested?

   ## Checklist
   - [ ] Tests pass
   - [ ] Code follows style guide
   - [ ] Documentation updated
   - [ ] No new warnings

   ## Related Issues
   Closes #123
   ```

3. **Review Process:**
   - Automated checks must pass
   - At least one approval required
   - Address feedback and re-request review

## Reporting Issues

### Bug Report Template
```markdown
## Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Python version
- OS
- FastAPI version

## Logs
```
Error logs or stack traces
```

## Attachments
Screenshot or log file
```

### Feature Request Template
```markdown
## Description
Clear description of feature

## Motivation
Why is this needed?

## Proposed Solution
How should it work?

## Alternative Approaches
Other ways to solve this?

## Additional Context
Any other information?
```

## Review Process

### For Maintainers
- Check code quality
- Verify tests pass
- Ensure documentation is updated
- Test functionality
- Provide constructive feedback
- Merge when ready

### For Contributors
- Respond to feedback
- Make requested changes
- Re-request review
- Be patient and respectful

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python PEP 8](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

## Questions?

- Open an issue for questions
- Check existing issues/discussions
- Ask in pull request comments
- Contact maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Intelligent Log Analyzer! 🚀
