import pandas as pd

VALID_TYPES = {"income", "expense"}

def transform_transactions(raw: pd.DataFrame):
    """Standardize values and return (cleaned_records, validation_issues)."""
    df = raw.copy()
    issues = []

    # Normalize text fields.
    for col in ["transaction_id", "description", "category", "type"]:
        df[col] = df[col].fillna("").astype(str).str.strip()

    df["type"] = df["type"].str.lower()
    df["category"] = df["category"].str.strip().str.title()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # Keep original row numbers to help locate issues in the source workbook.
    df["source_excel_row"] = range(2, len(df) + 2)

    missing_id = df["transaction_id"].eq("")
    for _, row in df[missing_id].iterrows():
        issues.append({"source_excel_row": int(row["source_excel_row"]),
                       "transaction_id": "", "issue": "Missing transaction_id",
                       "severity": "High"})

    missing_date = df["date"].isna()
    for _, row in df[missing_date].iterrows():
        issues.append({"source_excel_row": int(row["source_excel_row"]),
                       "transaction_id": row["transaction_id"], "issue": "Missing or invalid date",
                       "severity": "High"})

    invalid_amount = df["amount"].isna() | (df["amount"] <= 0)
    for _, row in df[invalid_amount].iterrows():
        issues.append({"source_excel_row": int(row["source_excel_row"]),
                       "transaction_id": row["transaction_id"], "issue": "Missing, invalid, zero or negative amount",
                       "severity": "High"})

    invalid_type = ~df["type"].isin(VALID_TYPES)
    for _, row in df[invalid_type].iterrows():
        issues.append({"source_excel_row": int(row["source_excel_row"]),
                       "transaction_id": row["transaction_id"], "issue": "Type must be income or expense",
                       "severity": "High"})

    missing_description = df["description"].eq("")
    for _, row in df[missing_description].iterrows():
        issues.append({"source_excel_row": int(row["source_excel_row"]),
                       "transaction_id": row["transaction_id"], "issue": "Missing description",
                       "severity": "Medium"})

    missing_category = df["category"].eq("")
    for _, row in df[missing_category].iterrows():
        issues.append({"source_excel_row": int(row["source_excel_row"]),
                       "transaction_id": row["transaction_id"], "issue": "Missing category",
                       "severity": "Medium"})

    future_date = df["date"].notna() & (df["date"] > pd.Timestamp.now().normalize())
    for _, row in df[future_date].iterrows():
        issues.append({"source_excel_row": int(row["source_excel_row"]),
                       "transaction_id": row["transaction_id"], "issue": "Future-dated transaction",
                       "severity": "Medium"})

    # A valid row must pass the core fields. Rows with medium issues remain in the
    # financial totals if the required transaction fields are valid.
    valid = (
        df["transaction_id"].ne("") &
        df["date"].notna() &
        df["amount"].notna() &
        (df["amount"] > 0) &
        df["type"].isin(VALID_TYPES)
    )
    cleaned = df.loc[valid].copy()
    cleaned["signed_amount"] = cleaned.apply(
        lambda r: r["amount"] if r["type"] == "income" else -r["amount"], axis=1
    )
    return cleaned, pd.DataFrame(issues, columns=[
        "source_excel_row", "transaction_id", "issue", "severity"
    ])
