# 04. Persistence and State

Rules for data management and pipeline resumability.

## 1. CsvStore Pattern
- **Inheritance:** Every `CsvStore` must inherit from `BaseModelTool`.
- **Core Processor:** Use `tools.common.csv_processor.CsvProcessor` for file operations (reading, updating, appending).
- **Column Management:** Define a `Column` Enum to handle CSV headers and row dictionary keys.
- **Mapping:** Implement a `_map_row` helper method to cross-reference CSV fields with Pydantic model attributes (e.g., using `model_validate_json` for complex fields).
- **Storage:** The `CsvStore` handles the path construction (using `os.path.join`) and initialization of the processor.

## 2. State Machine
- Use a `State` Enum to track the lifecycle of a processing unit.
- Every successful method execution must update the unit state in CSV.
- Pipelines must be designed to be "resumable": skip units that already have the target state.

## 3. Data Integrity
- Validate presence of required columns during `CsvStore` initialization.
- Fail early if the CSV structure is corrupted.
