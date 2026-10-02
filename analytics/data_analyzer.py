from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


# ============================================================
# FILE LOADING
# ============================================================

def load(path: str | Path) -> pd.DataFrame:
    """
    Load a supported business dataset.

    Supported:
        - CSV
        - XLSX

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: for unsupported file types or empty datasets.
    """

    p = Path(path)

    if not p.exists():
        raise FileNotFoundError(
            f"Dataset file not found: {p}"
        )

    suffix = p.suffix.lower()

    if suffix == ".csv":
        df = pd.read_csv(p)

    elif suffix == ".xlsx":
        df = pd.read_excel(p)

    else:
        raise ValueError(
            "Only CSV and XLSX datasets are supported."
        )

    if df.empty:
        raise ValueError(
            f"Dataset '{p.name}' contains no rows."
        )

    # Normalize column names without destroying their meaning.
    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    return df


# ============================================================
# BASIC SUMMARY
# ============================================================

def summary(df: pd.DataFrame) -> dict[str, Any]:
    """
    Return deterministic dataset-level statistics.
    """

    numeric = df.select_dtypes(include="number")
    categorical = df.select_dtypes(exclude="number")

    missing_by_column = {
        str(column): int(count)
        for column, count in df.isna().sum().items()
        if int(count) > 0
    }

    duplicate_rows = int(
        df.duplicated().sum()
    )

    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "missing": int(df.isna().sum().sum()),
        "missing_by_column": missing_by_column,
        "duplicates": duplicate_rows,
        "numeric": [
            str(column)
            for column in numeric.columns
        ],
        "categorical": [
            str(column)
            for column in categorical.columns
        ],
        "memory_mb": round(
            float(
                df.memory_usage(deep=True).sum()
            ) / 1_048_576,
            2,
        ),
    }


# ============================================================
# DATE DETECTION
# ============================================================

def _date_columns(df: pd.DataFrame) -> list[str]:
    """
    Detect columns that can reliably represent dates.

    Existing datetime columns are accepted directly.
    Object/string columns are accepted only when most values
    can be parsed as dates.
    """

    found: list[str] = []

    for column in df.columns:

        series = df[column]

        if pd.api.types.is_datetime64_any_dtype(series):
            found.append(str(column))
            continue

        if series.dtype == object:

            try:
                parsed = pd.to_datetime(
                    series,
                    format="mixed",
                    errors="coerce",
                )
            except (TypeError, ValueError):
                continue

            non_null = series.notna().sum()

            if non_null == 0:
                continue

            valid_ratio = (
                parsed.notna().sum() / non_null
            )

            if (
                valid_ratio >= 0.8
                and parsed.nunique(dropna=True) > 2
            ):
                found.append(str(column))

    return found


# ============================================================
# COLUMN DETECTION HELPERS
# ============================================================

def _find_column(
    columns: list[str],
    keywords: tuple[str, ...],
) -> str | None:
    """
    Find the first column whose name contains one of the
    supplied semantic keywords.
    """

    normalized = [
        (str(column), str(column).lower().strip())
        for column in columns
    ]

    for keyword in keywords:

        for original, lowered in normalized:

            if keyword in lowered:
                return original

    return None


def _find_numeric_columns(
    df: pd.DataFrame,
) -> list[str]:
    return [
        str(column)
        for column in df.select_dtypes(
            include="number"
        ).columns
    ]


def _find_value_columns(
    df: pd.DataFrame,
) -> dict[str, str | None]:

    columns = [
        str(column)
        for column in df.columns
    ]

    return {
        "revenue": _find_column(
            columns,
            (
                "revenue",
                "sales",
                "turnover",
                "amount",
                "total_sales",
            ),
        ),
        "profit": _find_column(
            columns,
            (
                "profit",
                "net_profit",
                "gross_profit",
                "earnings",
            ),
        ),
        "cost": _find_column(
            columns,
            (
                "cost",
                "expense",
                "spend",
                "unit_cost",
            ),
        ),
        "units": _find_column(
            columns,
            (
                "units",
                "quantity",
                "qty",
                "volume",
            ),
        ),
        "product": _find_column(
            columns,
            (
                "product",
                "item",
                "sku",
                "product_name",
            ),
        ),
        "category": _find_column(
            columns,
            (
                "category",
                "segment",
                "type",
            ),
        ),
        "region": _find_column(
            columns,
            (
                "region",
                "territory",
                "location",
                "market",
            ),
        ),
    }


# ============================================================
# NUMERIC CLEANING
# ============================================================

def _numeric_series(
    df: pd.DataFrame,
    column: str | None,
) -> pd.Series | None:

    if not column or column not in df.columns:
        return None

    return pd.to_numeric(
        df[column],
        errors="coerce",
    )


# ============================================================
# MONTHLY TREND
# ============================================================

def _monthly_trend(
    df: pd.DataFrame,
    date_column: str | None,
    value_column: str | None,
) -> dict[str, Any] | None:

    if (
        not date_column
        or not value_column
        or date_column not in df.columns
        or value_column not in df.columns
    ):
        return None

    dates = pd.to_datetime(
        df[date_column],
        errors="coerce",
    )

    values = pd.to_numeric(
        df[value_column],
        errors="coerce",
    )

    temp = pd.DataFrame(
        {
            "date": dates,
            "value": values,
        }
    ).dropna()

    if len(temp) < 2:
        return None

    temp["period"] = (
        temp["date"]
        .dt.to_period("M")
        .astype(str)
    )

    grouped = (
        temp.groupby(
            "period",
            as_index=False,
        )["value"]
        .sum()
    )

    if grouped.empty:
        return None

    records = [
        {
            "period": str(row["period"]),
            "value": round(
                float(row["value"]),
                2,
            ),
        }
        for _, row in grouped.iterrows()
    ]

    first_value = float(
        grouped.iloc[0]["value"]
    )

    last_value = float(
        grouped.iloc[-1]["value"]
    )

    if first_value != 0:
        change_pct = (
            (last_value - first_value)
            / abs(first_value)
            * 100
        )
    else:
        change_pct = 0.0

    return {
        "date_column": date_column,
        "value_column": value_column,
        "records": records,
        "first_period": str(
            grouped.iloc[0]["period"]
        ),
        "last_period": str(
            grouped.iloc[-1]["period"]
        ),
        "first_value": round(
            first_value,
            2,
        ),
        "last_value": round(
            last_value,
            2,
        ),
        "change_percent": round(
            float(change_pct),
            2,
        ),
    }


# ============================================================
# GROUPED BUSINESS ANALYSIS
# ============================================================

def _group_analysis(
    df: pd.DataFrame,
    group_column: str | None,
    value_column: str | None,
    top_n: int = 10,
) -> dict[str, Any] | None:

    if (
        not group_column
        or not value_column
        or group_column not in df.columns
        or value_column not in df.columns
    ):
        return None

    values = pd.to_numeric(
        df[value_column],
        errors="coerce",
    )

    temp = pd.DataFrame(
        {
            "group": df[group_column],
            "value": values,
        }
    ).dropna()

    if temp.empty:
        return None

    grouped = (
        temp.groupby(
            "group",
            as_index=False,
        )["value"]
        .sum()
        .sort_values(
            "value",
            ascending=False,
        )
        .head(top_n)
    )

    if grouped.empty:
        return None

    records = [
        {
            "group": str(row["group"]),
            "value": round(
                float(row["value"]),
                2,
            ),
        }
        for _, row in grouped.iterrows()
    ]

    return {
        "group_column": group_column,
        "value_column": value_column,
        "records": records,
    }


# ============================================================
# PROFITABILITY
# ============================================================

def _profitability(
    df: pd.DataFrame,
    value_columns: dict[str, str | None],
) -> dict[str, Any] | None:

    revenue_column = value_columns.get(
        "revenue"
    )

    profit_column = value_columns.get(
        "profit"
    )

    cost_column = value_columns.get(
        "cost"
    )

    revenue = _numeric_series(
        df,
        revenue_column,
    )

    profit = _numeric_series(
        df,
        profit_column,
    )

    cost = _numeric_series(
        df,
        cost_column,
    )

    if revenue is None:
        return None

    total_revenue = float(
        revenue.sum()
    )

    output: dict[str, Any] = {
        "revenue_column": revenue_column,
        "profit_column": profit_column,
        "cost_column": cost_column,
        "total_revenue": round(
            total_revenue,
            2,
        ),
    }

    if profit is not None:

        total_profit = float(
            profit.sum()
        )

        output["total_profit"] = round(
            total_profit,
            2,
        )

        if total_revenue != 0:
            output["profit_margin_percent"] = round(
                (
                    total_profit
                    / total_revenue
                    * 100
                ),
                2,
            )

    elif cost is not None:

        total_cost = float(
            cost.sum()
        )

        output["total_cost"] = round(
            total_cost,
            2,
        )

        calculated_profit = (
            total_revenue - total_cost
        )

        output["calculated_profit"] = round(
            calculated_profit,
            2,
        )

        if total_revenue != 0:
            output["calculated_profit_margin_percent"] = round(
                (
                    calculated_profit
                    / total_revenue
                    * 100
                ),
                2,
            )

    return output


# ============================================================
# CORRELATION ANALYSIS
# ============================================================

def _correlations(
    df: pd.DataFrame,
    top_n: int = 5,
) -> list[dict[str, Any]]:

    numeric = df.select_dtypes(
        include="number"
    )

    if numeric.shape[1] < 2:
        return []

    corr = numeric.corr(
        numeric_only=True
    )

    pairs: list[dict[str, Any]] = []

    columns = list(corr.columns)

    for index, first in enumerate(columns):

        for second in columns[index + 1:]:

            value = corr.loc[
                first,
                second,
            ]

            if pd.isna(value):
                continue

            pairs.append(
                {
                    "column_a": str(first),
                    "column_b": str(second),
                    "correlation": round(
                        float(value),
                        3,
                    ),
                    "absolute_correlation": round(
                        abs(float(value)),
                        3,
                    ),
                }
            )

    pairs.sort(
        key=lambda item: item[
            "absolute_correlation"
        ],
        reverse=True,
    )

    return pairs[:top_n]


# ============================================================
# DATA QUALITY
# ============================================================

def _quality_checks(
    df: pd.DataFrame,
) -> dict[str, Any]:

    missing_by_column = {
        str(column): int(count)
        for column, count in df.isna().sum().items()
        if int(count) > 0
    }

    duplicate_rows = int(
        df.duplicated().sum()
    )

    constant_columns = []

    for column in df.columns:

        try:
            if df[column].nunique(
                dropna=True
            ) <= 1:
                constant_columns.append(
                    str(column)
                )
        except Exception:
            continue

    return {
        "missing_cells": int(
            df.isna().sum().sum()
        ),
        "missing_by_column": missing_by_column,
        "duplicate_rows": duplicate_rows,
        "constant_columns": constant_columns,
    }


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze(
    df: pd.DataFrame,
    query: str = "",
) -> dict[str, Any]:
    """
    Perform deterministic business/data intelligence.

    The function never fabricates values.
    All metrics are calculated directly from the dataframe.
    """

    if df is None:
        raise ValueError(
            "No dataframe was supplied."
        )

    if df.empty:
        raise ValueError(
            "Cannot analyze an empty dataset."
        )

    q = (query or "").lower().strip()

    s = summary(df)

    numeric_columns = _find_numeric_columns(
        df
    )

    dates = _date_columns(df)

    value_columns = _find_value_columns(
        df
    )

    quality = _quality_checks(df)

    insights: list[str] = []

    metrics: dict[str, Any] = {
        "Rows": s["rows"],
        "Columns": s["columns"],
        "Missing cells": s["missing"],
        "Duplicate rows": s["duplicates"],
    }

    # --------------------------------------------------------
    # BASIC NUMERIC METRICS
    # --------------------------------------------------------

    for column in numeric_columns[:12]:

        series = pd.to_numeric(
            df[column],
            errors="coerce",
        ).dropna()

        if series.empty:
            continue

        lower = column.lower()

        if any(
            keyword in lower
            for keyword in (
                "revenue",
                "sales",
                "amount",
                "profit",
                "cost",
            )
        ):
            metrics[column] = round(
                float(series.sum()),
                2,
            )

        else:
            metrics[column] = round(
                float(series.mean()),
                2,
            )

    # --------------------------------------------------------
    # BUSINESS VALUE DETECTION
    # --------------------------------------------------------

    profitability = _profitability(
        df,
        value_columns,
    )

    if profitability:

        if "total_revenue" in profitability:

            metrics["Total Revenue"] = (
                profitability[
                    "total_revenue"
                ]
            )

            insights.append(
                "Total revenue calculated from "
                f"{profitability['revenue_column']}."
            )

        if "total_profit" in profitability:

            metrics["Total Profit"] = (
                profitability[
                    "total_profit"
                ]
            )

            margin = profitability.get(
                "profit_margin_percent"
            )

            if margin is not None:

                metrics["Profit Margin %"] = (
                    margin
                )

                insights.append(
                    "Profit margin calculated as "
                    "total profit divided by total "
                    "revenue."
                )

        elif "calculated_profit" in profitability:

            metrics["Calculated Profit"] = (
                profitability[
                    "calculated_profit"
                ]
            )

            margin = profitability.get(
                "calculated_profit_margin_percent"
            )

            if margin is not None:

                metrics[
                    "Calculated Profit Margin %"
                ] = margin

                insights.append(
                    "Calculated profit derived as "
                    "revenue minus cost."
                )

    # --------------------------------------------------------
    # MONTHLY TREND
    # --------------------------------------------------------

    date_column = dates[0] if dates else None

    revenue_column = value_columns.get(
        "revenue"
    )

    trend_value_column = (
        revenue_column
        or value_columns.get("profit")
        or (
            numeric_columns[0]
            if numeric_columns
            else None
        )
    )

    monthly_trend = _monthly_trend(
        df,
        date_column,
        trend_value_column,
    )

    if monthly_trend:

        first_value = monthly_trend[
            "first_value"
        ]

        last_value = monthly_trend[
            "last_value"
        ]

        change = monthly_trend[
            "change_percent"
        ]

        insights.append(
            f"{monthly_trend['value_column']} "
            f"changed {change:+.1f}% from "
            f"{monthly_trend['first_period']} "
            f"to {monthly_trend['last_period']}."
        )

        if last_value > first_value:
            insights.append(
                "The observed period ended above "
                "the starting period."
            )

        elif last_value < first_value:
            insights.append(
                "The observed period ended below "
                "the starting period."
            )

    # --------------------------------------------------------
    # TOP PRODUCT
    # --------------------------------------------------------

    product_column = value_columns.get(
        "product"
    )

    product_analysis = _group_analysis(
        df,
        product_column,
        revenue_column,
    )

    if product_analysis:

        records = product_analysis[
            "records"
        ]

        if records:

            top_product = records[0]

            insights.append(
                f"Highest revenue contribution "
                f"among detected products: "
                f"{top_product['group']} "
                f"({top_product['value']:,.2f})."
            )

    # --------------------------------------------------------
    # CATEGORY ANALYSIS
    # --------------------------------------------------------

    category_column = value_columns.get(
        "category"
    )

    category_analysis = _group_analysis(
        df,
        category_column,
        revenue_column,
    )

    if category_analysis:

        records = category_analysis[
            "records"
        ]

        if records:

            top_category = records[0]

            insights.append(
                f"Highest revenue category: "
                f"{top_category['group']} "
                f"({top_category['value']:,.2f})."
            )

    # --------------------------------------------------------
    # REGION ANALYSIS
    # --------------------------------------------------------

    region_column = value_columns.get(
        "region"
    )

    region_analysis = _group_analysis(
        df,
        region_column,
        revenue_column,
    )

    if region_analysis:

        records = region_analysis[
            "records"
        ]

        if records:

            top_region = records[0]

            insights.append(
                f"Highest revenue region: "
                f"{top_region['group']} "
                f"({top_region['value']:,.2f})."
            )

    # --------------------------------------------------------
    # DATA QUALITY INSIGHTS
    # --------------------------------------------------------

    if quality["missing_cells"]:

        insights.append(
            f"Data quality: "
            f"{quality['missing_cells']:,} "
            "missing cell(s) detected."
        )

    if quality["duplicate_rows"]:

        insights.append(
            f"Data quality: "
            f"{quality['duplicate_rows']:,} "
            "duplicate row(s) detected."
        )

    # --------------------------------------------------------
    # CORRELATION
    # --------------------------------------------------------

    correlations: list[dict[str, Any]] = []

    if (
        "correlation" in q
        or "relationship" in q
        or "correlate" in q
    ):

        correlations = _correlations(
            df
        )

        for pair in correlations[:3]:

            insights.append(
                f"Correlation between "
                f"{pair['column_a']} and "
                f"{pair['column_b']}: "
                f"{pair['correlation']:.2f}."
            )

    # --------------------------------------------------------
    # QUERY-SPECIFIC GROUP ANALYSIS
    # --------------------------------------------------------

    requested_group_analysis = None

    if (
        "product" in q
        and product_column
        and revenue_column
    ):

        requested_group_analysis = (
            product_analysis
        )

    elif (
        "category" in q
        and category_column
        and revenue_column
    ):

        requested_group_analysis = (
            category_analysis
        )

    elif (
        "region" in q
        and region_column
        and revenue_column
    ):

        requested_group_analysis = (
            region_analysis
        )

    # --------------------------------------------------------
    # RETURN COMPLETE ANALYSIS PACKAGE
    # --------------------------------------------------------

    return {
        "summary": s,

        "metrics": metrics,

        "insights": insights,

        "date_columns": dates,

        "detected_columns": value_columns,

        "monthly_trend": monthly_trend,

        "product_analysis": product_analysis,

        "category_analysis": category_analysis,

        "region_analysis": region_analysis,

        "profitability": profitability,

        "correlations": correlations,

        "requested_group_analysis": (
            requested_group_analysis
        ),

        "data_quality": quality,

        "query": query,

        "calculation_basis": {
            "source": "uploaded_dataframe",
            "deterministic": True,
            "fabricated_values": False,
        },
    }