import pandas as pd

def run_audit(cleaned: pd.DataFrame, validation_issues: pd.DataFrame, total_source_rows=None):
    """Return audit summary metrics and a transaction-level findings table."""
    findings = []

    # Duplicate transaction IDs.
    duplicate_mask = cleaned["transaction_id"].duplicated(keep=False)
    for _, row in cleaned[duplicate_mask].iterrows():
        findings.append({
            "source_excel_row": int(row["source_excel_row"]),
            "transaction_id": row["transaction_id"],
            "date": row["date"],
            "description": row["description"],
            "amount": row["amount"],
            "type": row["type"],
            "finding": "Duplicate transaction ID",
            "severity": "High"
        })

    # Exact duplicate transaction details, even if IDs differ.
    exact_cols = ["date", "description", "amount", "type"]
    exact_mask = cleaned.duplicated(subset=exact_cols, keep=False)
    for _, row in cleaned[exact_mask].iterrows():
        findings.append({
            "source_excel_row": int(row["source_excel_row"]),
            "transaction_id": row["transaction_id"],
            "date": row["date"],
            "description": row["description"],
            "amount": row["amount"],
            "type": row["type"],
            "finding": "Possible duplicate transaction details",
            "severity": "Medium"
        })

    # Flag unusually large amounts using a simple statistical screening rule.
    # This is a review signal, not proof of fraud or an accounting error.
    if len(cleaned) >= 5:
        median = cleaned["amount"].median()
        if pd.notna(median) and median > 0:
            threshold = max(median * 3, cleaned["amount"].quantile(0.99))
            unusual = cleaned[cleaned["amount"] > threshold]
            for _, row in unusual.iterrows():
                findings.append({
                    "source_excel_row": int(row["source_excel_row"]),
                    "transaction_id": row["transaction_id"],
                    "date": row["date"],
                    "description": row["description"],
                    "amount": row["amount"],
                    "type": row["type"],
                    "finding": f"Unusually large amount (review threshold: {threshold:.2f})",
                    "severity": "Medium"
                })

    findings_df = pd.DataFrame(findings, columns=[
        "source_excel_row", "transaction_id", "date", "description",
        "amount", "type", "finding", "severity"
    ])

    income = cleaned.loc[cleaned["type"] == "income", "amount"].sum()
    expenses = cleaned.loc[cleaned["type"] == "expense", "amount"].sum()
    summary = pd.DataFrame([
        {"metric": "Total source rows", "value": int(total_source_rows if total_source_rows is not None else len(cleaned))},
        {"metric": "Valid transactions included in totals", "value": int(len(cleaned))},
        {"metric": "Income total", "value": round(float(income), 2)},
        {"metric": "Expense total", "value": round(float(expenses), 2)},
        {"metric": "Net cash flow", "value": round(float(income - expenses), 2)},
        {"metric": "Validation issues", "value": int(len(validation_issues))},
        {"metric": "Audit findings", "value": int(len(findings_df))},
        {"metric": "Duplicate transaction IDs", "value": int(cleaned["transaction_id"].duplicated(keep=False).sum())},
    ])

    category_summary = (
        cleaned.groupby(["type", "category"], dropna=False)["amount"]
        .sum().reset_index().sort_values(["type", "amount"], ascending=[True, False])
    )
    return summary, findings_df, category_summary
