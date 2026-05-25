# Standard: storage_csv.py

Handles data persistence using the repository's standard CSV tools.

## Requirements
- **Inheritance:** Inherit directly from `tools.common.csv_processor.CsvProcessor`.
- **Initialization:** Accept a `csv_path: Path` in the constructor. Pass it directly to the `CsvProcessor` super-constructor.
- **Simplified Schema:** Store only essential metadata (ID, State, Title, Category). Full script details must be stored in sidecar JSON files.
- **Column Enum:** Define a `Column(str, Enum)` for all CSV headers.
- **Strict Mode:** Use `cast(Any, df.index)` or `cast(Any, df[Column.STATE.value])` for Pandas lookups to avoid "partially unknown" member errors.
- **Mapping:** Use a `_map_row` method for clean object reconstruction.

## Standard Methods
- `get_next_id() -> int`: Returns the next available auto-incremented ID.
- `get_first_by_state(state: State) -> Model | None`: Finds the first project ready for the next pipeline step.
- `add_new_idea(title: str, category: Category) -> Model`: Initializes a new tracking row.
- `save(idea_obj: Model) -> None`: Updates an existing row's metadata and state.

## Example
```python
from pathlib import Path
from typing import Any, cast
from enum import Enum
from tools.common.csv_processor import CsvProcessor

class Column(str, Enum):
    ID = "id"
    TITLE = "title"
    STATE = "state"

class CsvStore(CsvProcessor):
    def __init__(self, csv_path: Path):
        super().__init__(
            path=csv_path,
            required_columns=[col.value for col in Column]
        )

    def _map_row(self, row: Any) -> VideoIdea:
        return VideoIdea(
            id=int(row[Column.ID.value]),
            title=row[Column.TITLE.value],
            state=row[Column.STATE.value]
        )

    def get_first_by_state(self, state: State) -> VideoIdea | None:
        df = self.read_all()
        # Strict mode pattern
        idx = cast(Any, df.index)[df[Column.STATE.value] == state.value]
        if len(idx) == 0:
            return None
        return self.get_by_index(int(idx[0]))
```
