from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = ["transaction_id", "date", "description", "category", "type", "amount"]

def extract_transactions(file_path: str, sheet_name=0) -> pd.DataFrame:
    """Read transaction records from an Excel workbook."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Input workbook not found: {path}")

    df = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            "Missing required Excel columns: " + ", ".join(missing) +
            ". Use data/financial_template.xlsx as your template."
        )

    return df
