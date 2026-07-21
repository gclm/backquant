```markdown
# backquant Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches you the core development patterns and conventions used in the `backquant` Python codebase. You'll learn how to structure files, write imports and exports, and follow commit and testing conventions. This guide also provides step-by-step workflows and helpful commands to streamline your development process.

## Coding Conventions

### File Naming
- Use **snake_case** for all file names.
  - Example: `data_loader.py`, `strategy_test.py`

### Import Style
- Use **relative imports** within the package.
  - Example:
    ```python
    from .utils import calculate_returns
    ```

### Export Style
- Use **named exports** (explicitly define what is exported).
  - Example:
    ```python
    __all__ = ['BacktestEngine', 'Strategy']
    ```

### Commit Patterns
- Commit types are **mixed**, but documentation updates use the `docs` prefix.
- Example commit message:
  ```
  docs: update README with installation instructions
  ```
- Average commit message length: ~63 characters.

## Workflows

### Documentation Update
**Trigger:** When updating or adding documentation files.
**Command:** `/update-docs`

1. Make your documentation changes.
2. Stage your changes:
    ```
    git add docs/
    ```
3. Commit with the `docs:` prefix:
    ```
    git commit -m "docs: update API usage section"
    ```
4. Push your changes:
    ```
    git push
    ```

### Adding a New Module
**Trigger:** When adding a new feature or module.
**Command:** `/add-module`

1. Create a new Python file using snake_case (e.g., `new_feature.py`).
2. Use relative imports for dependencies within the package.
    ```python
    from .existing_module import helper_function
    ```
3. Explicitly define exports with `__all__`.
    ```python
    __all__ = ['NewFeature']
    ```
4. Write or update tests in a corresponding `*.test.*` file.
5. Commit your changes with a descriptive message.
    ```
    git commit -m "add new_feature module for advanced analytics"
    ```

### Running Tests
**Trigger:** When verifying code changes.
**Command:** `/run-tests`

1. Ensure your test files follow the `*.test.*` pattern (e.g., `strategy.test.py`).
2. Run your tests using your preferred test runner (framework not detected; use `pytest` or similar if available).
    ```
    pytest
    ```
3. Review test results and fix any issues.

## Testing Patterns

- Test files are named using the `*.test.*` pattern, such as `module.test.py`.
- The testing framework is **unknown**; you may use `pytest` or another standard Python test runner.
- Place tests alongside or near the modules they cover.

Example test file:
```python
# test_strategy.test.py
from .strategy import Strategy

def test_strategy_returns():
    s = Strategy()
    assert s.run() > 0
```

## Commands
| Command        | Purpose                                      |
|----------------|----------------------------------------------|
| /update-docs   | Update or add documentation files            |
| /add-module    | Add a new module following conventions       |
| /run-tests     | Run all tests in the codebase                |
```
