# VIBA - Daily Financial Audit (DFA)

A Python ETL and financial data-quality screening pipeline executed by GitHub Actions.

## What it does

1. **Extract:** reads transaction records from an Excel workbook.
2. **Transform:** standardizes fields and validates IDs, dates, amounts and transaction types.
3. **Audit:** flags duplicate IDs, possible duplicate transaction details and unusually large amounts.
4. **Load:** writes an Excel report containing summary metrics, findings, validation issues, category totals and processed transactions.

This is an automated screening tool, not a formal audit, fraud detector, accounting opinion or reconciliation against a bank statement.

## Excel input format

The input workbook must contain a worksheet with these required columns:

| Column | Description | Example |
|---|---|---|
| transaction_id | Unique transaction reference | TXN-1001 |
| date | Transaction date | 2026-10-01 |
| description | What the transaction was | Grocery store |
| category | Transaction category | Groceries |
| type | `income` or `expense` | expense |
| amount | Positive numeric amount | 42.50 |

Optional columns such as `account`, `reference`, and `notes` are retained in processed output.

Use `data/financial_template.xlsx` as the blank template. `data/sample_transactions.xlsx` contains fictional test records.

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python src/main.py
```

The report is written to `reports/`.

To use another workbook:

**Windows PowerShell**
```powershell
$env:FINANCIAL_INPUT="data/my_transactions.xlsx"
python src/main.py
```

**macOS/Linux**
```bash
FINANCIAL_INPUT=data/my_transactions.xlsx python src/main.py
```

## GitHub Actions

The workflow is `.github/workflows/DFA.yml`.

- Runs daily at 00:00 UTC.
- Can also be started manually from the repository's **Actions** tab using **Run workflow**.
- Uploads the generated workbook as an artifact for 30 days.

GitHub scheduled runs are not guaranteed to start at the exact minute. The default branch must contain the workflow file.

## Important: private financial data

The VIBA repository may be public. Do not commit personal, customer, bank or other confidential financial data.

The sample workbook and blank template are safe to commit. For real daily data, use a private repository or modify the extraction stage to retrieve the workbook securely from an approved private storage provider. Do not put passwords, access tokens or private financial records in source code or public Git history.

## Limitations and interpretation

- Excel worksheets are limited to 1,048,576 rows. Processing is also limited by available runner memory.
- Duplicate and unusual-amount flags require human review; they are not proof of error or fraud. Duplicate rows are flagged but are not automatically removed from financial totals, so review duplicates before relying on totals.
- The current workflow reads the workbook committed at `data/sample_transactions.xlsx`. It does not automatically fetch a newly updated workbook from a computer, Drive or OneDrive.
- The current version calculates income, expenses and net cash flow from the rows in the input workbook. It does not reconcile against bank balances unless opening/closing balances and an independent source are added.
