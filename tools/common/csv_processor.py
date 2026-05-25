from pathlib import Path
from typing import Any, Dict, List, cast

import pandas as pd

from tools.common.base_model import BaseModelTool

# TODO: solve casts


class CsvProcessor(BaseModelTool):
    """
    Generic tool for basic CSV operations using pandas.
    """
    path: Path
    required_columns: List[str]

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            df: Any = cast(Any, pd).DataFrame(columns=cast(Any, list(self.required_columns)))
            df.to_csv(self.path, index=False)
        else:
            self.validate_structure()

    def validate_structure(self) -> None:
        if not self.required_columns:
            return
        df = cast(Any, pd).read_csv(self.path)
        for col in self.required_columns:
            if col not in df.columns:
                raise ValueError(f"Invalid CSV structure at {self.path}. Missing column: {col}")

    def read_all(self) -> pd.DataFrame:
        return cast(pd.DataFrame, cast(Any, pd).read_csv(self.path))

    def write_all(self, df: pd.DataFrame) -> None:
        cast(Any, df).to_csv(self.path, index=False)

    def get_row(self, index: int) -> Dict[str, Any]:
        df = self.read_all()
        return cast(Dict[str, Any], cast(Any, df.iloc[index]).to_dict())

    def update_row(self, index: int, data: Dict[str, Any]) -> None:
        df = self.read_all()
        for key, value in data.items():
            # If the column is inferred as float (due to NaNs) but we are writing a string,
            # cast it to object to avoid FutureWarning.
            if cast(Any, df[key]).dtype == "float64" and isinstance(value, str):
                df[key] = cast(Any, df[key]).astype(object)
            df.at[index, key] = value
        self.write_all(df)

    def add_row(self, data: Dict[str, Any]) -> None:
        df = self.read_all()
        new_row = cast(Any, pd).DataFrame([data])
        df = cast(pd.DataFrame, cast(Any, pd).concat([df, new_row], ignore_index=True))
        self.write_all(df)
