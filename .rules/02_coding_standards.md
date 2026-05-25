# 02. Coding Standards

Python best practices for reliability and traceability.

## 1. Strict Typing & Validation
- Inherit all logic components from `BaseModelTool` (in `tools.common.base_model`).
- Define explicit `__init__` methods with clear parameters.
- Call `super().__init__(...)` after initializing internal variables.

## 2. Absolute Imports
- **MANDATORY**: All imports must be absolute from the root (e.g., `from tools.common...`).
- Never use relative imports (e.g., `from .module...`).

## 3. Immutables
- Use `Enum` for states, types, and column names.
- Use `Literal` for fixed string configurations.

## 4. Error Handling
- Use specific exceptions (e.g., `ValueError`, `FileNotFoundError`).
- Provide context in error messages including relevant paths or IDs.
