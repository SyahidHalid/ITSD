import pandas as pd
import numpy as np

from sklearn.model_selection import GroupShuffleSplit
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    average_precision_score
)
from sklearn.ensemble import HistGradientBoostingClassifier

# --------------------------------------------------
# 1. Load the main financing dataset
# --------------------------------------------------
df = pd.read_excel(
    r"D:\\00. Git Repository\\ITSD\\Unified Data Exchange\\UDX Python\\input\\MIS4_EXPANDED.xlsx",
    engine="openpyxl"
)

# Standardise column names
df.columns = (
    df.columns.astype(str)
    .str.strip()
    .str.upper()
    .str.replace(r"\s+", "_", regex=True)
    .str.replace(r"[^A-Z0-9_]", "", regex=True)
)

# --------------------------------------------------
# 2. Convert selected fields to numeric
# --------------------------------------------------
numeric_candidates = [
    "APPROVED_LIMIT",
    "CURRENT_LIMIT",
    "TOTAL_OUTSTANDING_A",
    "TOTAL_OVERDUE",
    "OVERDUE_DAYS",
    "LAST_MTH_OVERDUE_DAYS",
    "THIS_MONTH_PAY",
    "YEAR_TO_DATE_COLLECTION",
    "TOTAL_COLLECTION",
    "TOTAL_DUE",
    "PRINCIPAL_BALANCE",
    "PRINCIPAL_OVERDUE",
    "PROFIT_BALANCE",
    "UNDRAWN",
    "PROFIT_RATE",
    "REMAINING_TENURE",
    "CHARGEOFF_AMOUNT"
]

for col in numeric_candidates:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Helper to find the actual standardised column
def first_existing(columns):
    for col in columns:
        if col in df.columns:
            return col
    return None

outstanding_col = first_existing([
    "TOTAL_OUTSTANDING_A",
    "FINAL_TOTAL_OUSTANDING_CA_B"
])

approved_col = first_existing(["APPROVED_LIMIT"])
overdue_col = first_existing(["TOTAL_OVERDUE"])
due_col = first_existing(["TOTAL_DUE"])
collection_col = first_existing(["TOTAL_COLLECTION"])
principal_col = first_existing(["PRINCIPAL_BALANCE"])
principal_overdue_col = first_existing(["PRINCIPAL_OVERDUE"])

# --------------------------------------------------
# 3. Feature engineering
# --------------------------------------------------
def safe_ratio(numerator, denominator):
    denominator = denominator.replace(0, np.nan)
    return numerator / denominator

if outstanding_col and approved_col:
    df["UTILISATION_RATIO"] = safe_ratio(
        df[outstanding_col], df[approved_col]
    )

if overdue_col and outstanding_col:
    df["OVERDUE_RATIO"] = safe_ratio(
        df[overdue_col], df[outstanding_col]
    )

if collection_col and due_col:
    df["COLLECTION_RATIO"] = safe_ratio(
        df[collection_col], df[due_col]
    )

if principal_overdue_col and principal_col:
    df["PRINCIPAL_OVERDUE_RATIO"] = safe_ratio(
        df[principal_overdue_col], df[principal_col]
    )

# --------------------------------------------------
# 4. Create a provisional target
# Replace this with a future-period outcome
# --------------------------------------------------
status = df.get(
    "STATUS_REPORTING",
    pd.Series("", index=df.index)
).astype(str).str.upper()

overdue_days = pd.to_numeric(
    df.get("OVERDUE_DAYS", 0),
    errors="coerce"
).fillna(0)

chargeoff = pd.to_numeric(
    df.get("CHARGEOFF_AMOUNT", 0),
    errors="coerce"
).fillna(0)

df["HIGH_RISK"] = (
    status.eq("IMPAIRED")
    | overdue_days.ge(90)
    | chargeoff.gt(0)
).astype(int)

# --------------------------------------------------
# 5. Select model features
# Exclude post-outcome fields where necessary
# --------------------------------------------------
candidate_features = [
    "TYPE_OF_FINANCING",
    "FUND_CONTROL",
    "GROUP_OF_FUND",
    "PRODUCT_CATEGORY",
    "FINANCING_CONCEPT",
    "APPROVED_LIMIT",
    "CURRENT_LIMIT",
    outstanding_col,
    "PRINCIPAL_BALANCE",
    "TOTAL_OVERDUE",
    "LAST_MTH_OVERDUE_DAYS",
    "THIS_MONTH_PAY",
    "YEAR_TO_DATE_COLLECTION",
    "TOTAL_COLLECTION",
    "UNDRAWN",
    "REPAYMENT_FREQUENCY",
    "PROFIT_RATE",
    "REMAINING_TENURE",
    "INDUSTRY_TYPE",
    "INDUSTRY_SECTOR",
    "SME_CATEGORY",
    "STATE_CODE",
    "CUSTOMER_SEGMENTAION",
    "UTILISATION_RATIO",
    "OVERDUE_RATIO",
    "COLLECTION_RATIO",
    "PRINCIPAL_OVERDUE_RATIO"
]

features = [
    col for col in candidate_features
    if col is not None and col in df.columns
]

X = df[features].copy()
y = df["HIGH_RISK"]

numeric_features = X.select_dtypes(
    include=["number"]
).columns.tolist()

categorical_features = [
    col for col in X.columns
    if col not in numeric_features
]

# --------------------------------------------------
# 6. Preprocessing and model
# --------------------------------------------------
preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            SimpleImputer(strategy="median"),
            numeric_features
        ),
        (
            "categorical",
            Pipeline(
                steps=[
                    (
                        "imputer",
                        SimpleImputer(strategy="most_frequent")
                    ),
                    (
                        "encoder",
                        OneHotEncoder(
                            handle_unknown="ignore",
                            min_frequency=2
                        )
                    )
                ]
            ),
            categorical_features
        )
    ]
)

model = HistGradientBoostingClassifier(
    learning_rate=0.05,
    max_iter=300,
    max_leaf_nodes=15,
    min_samples_leaf=10,
    class_weight="balanced",
    random_state=42
)

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)

# --------------------------------------------------
# 7. Customer-level split to prevent leakage
# --------------------------------------------------
group_col = first_existing([
    "CIF_NUMBER",
    "CUSTOMER_NAME"
])

groups = (
    df[group_col].astype(str)
    if group_col
    else pd.Series(df.index, index=df.index)
)

splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=42
)

train_index, test_index = next(
    splitter.split(X, y, groups)
)

X_train = X.iloc[train_index]
X_test = X.iloc[test_index]
y_train = y.iloc[train_index]
y_test = y.iloc[test_index]

pipeline.fit(X_train, y_train)

predicted_probability = pipeline.predict_proba(X_test)[:, 1]
predicted_class = (predicted_probability >= 0.50).astype(int)

print(classification_report(y_test, predicted_class))
print("ROC-AUC:", roc_auc_score(y_test, predicted_probability))
print(
    "PR-AUC:",
    average_precision_score(y_test, predicted_probability)
)

# --------------------------------------------------
# 8. Produce risk scores
# --------------------------------------------------
results = df.iloc[test_index][
    [col for col in ["CIF_NUMBER", "CUSTOMER_NAME"]
     if col in df.columns]
].copy()

results["ACTUAL_HIGH_RISK"] = y_test.to_numpy()
results["RISK_PROBABILITY"] = predicted_probability

results["RISK_BAND"] = pd.cut(
    results["RISK_PROBABILITY"],
    bins=[-0.01, 0.30, 0.60, 1.00],
    labels=["LOW", "MEDIUM", "HIGH"]
)

results = results.sort_values(
    "RISK_PROBABILITY",
    ascending=False
)

results.to_excel(
    r"D:\\00. Git Repository\\ITSD\\Unified Data Exchange\\UDX Python\\output\\customer_risk_predictions.xlsx",
    index=False,
    engine="openpyxl"
)

print(results.head(20))