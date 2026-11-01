from pathlib import Path
from datetime import datetime, timezone
import os
import pandas as pd

from extract import extract_transactions
from transform import transform_transactions
from audit import run_audit

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = Path(os.getenv("FINANCIAL_INPUT", ROOT / "data" / "sample_transactions.xlsx"))
REPORT_DIR = Path(os.getenv("REPORT_DIR", ROOT / "reports"))

def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Starting financial audit: {INPUT_FILE}")

    raw = extract_transactions(str(INPUT_FILE))
    cleaned, validation_issues = transform_transactions(raw)
    summary, findings, category_summary = run_audit(cleaned, validation_issues, total_source_rows=len(raw))

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")
    report_path = REPORT_DIR / f"financial_audit_{timestamp}.xlsx"

    with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="Audit Summary", index=False)
        findings.to_excel(writer, sheet_name="Audit Findings", index=False)
        validation_issues.to_excel(writer, sheet_name="Validation Issues", index=False)
        category_summary.to_excel(writer, sheet_name="Category Summary", index=False)
        cleaned.to_excel(writer, sheet_name="Processed Transactions", index=False)

        for ws in writer.book.worksheets:
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            for column_cells in ws.columns:
                max_len = max((len(str(c.value)) if c.value is not None else 0)
                              for c in column_cells)
                ws.column_dimensions[column_cells[0].column_letter].width = min(max(max_len + 2, 12), 45)

    print("\nAUDIT SUMMARY")
    print(summary.to_string(index=False))
    print(f"\nReport created: {report_path}")
    print("Audit completed.")

if __name__ == "__main__":
    main()
