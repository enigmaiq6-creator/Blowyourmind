# 03. Documentation and Logging

Standards for explaining code and providing terminal feedback.

## 1. Method Docstrings

### Case A: Simple Helpers
For simple methods, a single-paragraph docstring is sufficient:
```python
def get_idea_path(self, idea_id: int) -> Path:
    """
    Returns the absolute path to an idea's folder.
    """
```

### Case B: Multi-Step Logic
For complex logic (pipeline steps, complex processing), follow the numbered pattern:
```python
def my_step(self):
    """
    Title: Summary.
    1. Technical step one.
    2. Technical step two.
    """
```

## 2. In-Code Demarcation
For multi-step logic, use numbered comments that match the docstring exactly:
```python
# 1. Technical step one.
logic_here()
```

## 3. Terminal Messenger
Use `tools.common.messenger.Messenger` exclusively:
- `.info()`: Descriptive progress.
- `.success()`: Minor task done (🚀).
- `.step_success()`: Pipeline milestone (✅).
- `.image()`: Asset generation (🖼️).
- `.error()`: Fatal failure (❌).
