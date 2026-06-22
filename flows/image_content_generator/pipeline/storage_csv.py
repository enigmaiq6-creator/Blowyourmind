from enum import Enum
from pathlib import Path
from typing import Any, cast

import pandas as pd

from flows.image_content_generator.pipeline.schemas import IdeaRaw, State
from tools.common.csv_processor import CsvProcessor


class Column(str, Enum):
    ID = "id"
    TITLE = "title"
    STATE = "state"
    CATEGORY = "category"

# TODO: Solve casts


class CsvStore(CsvProcessor):
    """
    Adapter for the CSV storage for Image Content Generator.
    """

    def __init__(self, csv_path: Path):
        super().__init__(
            path=csv_path,
            required_columns=[col.value for col in Column]
        )

    def get_by_index(self, index: int) -> IdeaRaw:
        row = self.get_row(index)
        return self._map_row(row)

    def get_first_by_state(self, state: State, category: str | None = None) -> IdeaRaw | None:
        df = self.read_all()
        if df.empty:
            return None

        # Filter by state
        matching_rows = df[df[Column.STATE.value] == state.value]
        if matching_rows.empty:
            return None

        # Optional category filter
        if category:
            matching_rows = matching_rows[matching_rows[Column.CATEGORY.value] == category]

        if matching_rows.empty:
            return None

        # IMPORTANT: Verify that the folder actually exists!
        # This prevents picking up 'stuck' ideas that were deleted by cleanup but remain in CSV
        for _, row in matching_rows.iterrows():
            idea_id = int(row[Column.ID.value])
            # CRITICAL FIX: The CSV is now in tracking/ folder (which is git-tracked),
            # but the actual media files and idea directories are generated in out_short/ (gitignored).
            # We must look at out_short/ideas/ rather than the parent of the CSV (which is tracking/ideas/).
            # The CSV path is always tracking/ideas_tracking.csv, so its parent is tracking/.
            # We want tracking/../out_short/ideas/ (or flows/image_content_generator/out_short/ideas/).
            out_base = self.path.parent.parent / "out_short"
            ideas_dir = out_base / "ideas"
            folder_name = f"idea_{idea_id:06d}"
            idea_path = ideas_dir / folder_name
            
            if idea_path.exists():
                return self._map_row(row)
        
        return None

    def get_all_titles(self) -> list[str]:
        df = self.read_all()
        if df.empty:
            return []
        return df[Column.TITLE.value].tolist()

    def get_next_id(self) -> int:
        df = self.read_all()
        if df.empty:
            return 1

        # Simplified casting: single Any cast on the series for max() lookup
        max_id = cast(Any, df[Column.ID.value]).max()
        return int(max_id) + 1

    def add_new_idea(self, title: str, category: str) -> IdeaRaw:
        new_id = self.get_next_id()

        row_data: dict[str, Any] = {
            Column.ID.value: new_id,
            Column.TITLE.value: title,
            Column.STATE.value: State.NEW.value,
            Column.CATEGORY.value: category,
        }
        self.add_row(row_data)
        return self._map_row(pd.Series(row_data))

    def save(self, idea_obj: IdeaRaw) -> None:
        df = self.read_all()

        # Simplified casting: single Any cast on the index for ID lookup
        idx = cast(Any, df.index)[df[Column.ID.value] == idea_obj.id]
        if len(idx) == 0:
            raise ValueError(f"No idea found in storage with ID: {idea_obj.id}")

        row_index = int(idx[0])

        row_data: dict[str, Any] = {
            Column.ID.value: idea_obj.id,
            Column.TITLE.value: idea_obj.title,
            Column.STATE.value: idea_obj.state.value,
            Column.CATEGORY.value: idea_obj.category
        }
        self.update_row(row_index, row_data)

    def update_state(self, idea_id: int, state: State) -> None:
        df = self.read_all()
        idx = cast(Any, df.index)[df[Column.ID.value] == idea_id]
        if len(idx) == 0:
            raise ValueError(f"No idea found in storage with ID: {idea_id}")
        
        row_index = int(idx[0])
        row_data = df.iloc[row_index].to_dict()
        row_data[Column.STATE.value] = state.value
        self.update_row(row_index, row_data)

    def _map_row(self, row: Any) -> IdeaRaw:
        idea_id = int(row[Column.ID.value])

        # Create the object
        idea_obj = IdeaRaw(
            id=idea_id,
            title=row[Column.TITLE.value],
            state=row[Column.STATE.value],
            category=row[Column.CATEGORY.value],
        )
        return idea_obj
