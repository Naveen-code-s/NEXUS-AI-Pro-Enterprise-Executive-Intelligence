from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px


def _detect_date_columns(df: pd.DataFrame) -> list[str]:
    """Detect columns containing meaningful date/time values."""
    date_columns: list[str] = []

    for column in df.columns:
        series = df[column]

        if pd.api.types.is_datetime64_any_dtype(series):
            date_columns.append(column)
            continue

        if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
            # Explicit format handling for common ISO dates.
            parsed = pd.to_datetime(
                series,
                format="mixed",
                errors="coerce",
            )

            valid_ratio = parsed.notna().mean()

            if valid_ratio >= 0.8 and parsed.nunique(dropna=True) > 1:
                date_columns.append(column)

    return date_columns


def _find_value_column(df: pd.DataFrame) -> str | None:
    """Find the most relevant numeric value column."""
    numeric_columns = df.select_dtypes(include="number").columns.tolist()

    if not numeric_columns:
        return None

    preferred_keywords = (
        "revenue",
        "sales",
        "profit",
        "amount",
        "value",
        "income",
        "cost",
        "price",
        "total",
    )

    for column in numeric_columns:
        name = str(column).lower()

        if any(keyword in name for keyword in preferred_keywords):
            return column

    return numeric_columns[0]


def _find_column(
    df: pd.DataFrame,
    keywords: tuple[str, ...],
    exclude: set[str] | None = None,
) -> str | None:
    """Find a column using semantic keywords."""
    excluded = exclude or set()

    for column in df.columns:
        if column in excluded:
            continue

        name = str(column).lower()

        if any(keyword in name for keyword in keywords):
            return column

    return None


def _safe_numeric(df: pd.DataFrame, column: str) -> pd.Series:
    """Safely convert a column to numeric values."""
    return pd.to_numeric(df[column], errors="coerce")


def build_charts(
    df: pd.DataFrame,
    query: str = "",
    max_charts: int = 3,
) -> list[dict[str, Any]]:
    """
    Build charts using only real dataframe columns and values.

    Public API:
        build_charts(df, query="", max_charts=3)
    """

    if df is None or not isinstance(df, pd.DataFrame):
        return []

    if df.empty or max_charts <= 0:
        return []

    query_text = str(query or "").lower()
    charts: list[dict[str, Any]] = []

    # ---------------------------------------------------------
    # 1. Detect date columns
    # ---------------------------------------------------------
    date_columns = _detect_date_columns(df)

    # ---------------------------------------------------------
    # 2. Detect numeric value column
    # ---------------------------------------------------------
    value_column = _find_value_column(df)

    # ---------------------------------------------------------
    # 3. Monthly trend
    # ---------------------------------------------------------
    if date_columns and value_column:
        date_column = date_columns[0]

        dates = pd.to_datetime(
            df[date_column],
            format="mixed",
            errors="coerce",
        )

        values = _safe_numeric(df, value_column)

        trend_df = pd.DataFrame(
            {
                "Date": dates,
                "Value": values,
            }
        ).dropna()

        if len(trend_df) >= 2:
            trend_df["Month"] = (
                trend_df["Date"]
                .dt.to_period("M")
                .astype(str)
            )

            monthly = (
                trend_df
                .groupby("Month", as_index=False)["Value"]
                .sum()
            )

            if len(monthly) >= 2:
                figure = px.line(
                    monthly,
                    x="Month",
                    y="Value",
                    markers=True,
                )

                charts.append(
                    {
                        "id": f"trend_{date_column}_{value_column}",
                        "title": f"Monthly trend — {value_column}",
                        "figure": figure,
                    }
                )

    # ---------------------------------------------------------
    # 4. Product comparison
    # ---------------------------------------------------------
    product_column = _find_column(
        df,
        (
            "product",
            "item",
            "sku",
            "model",
        ),
        exclude=set(date_columns),
    )

    if product_column and value_column:
        product_df = pd.DataFrame(
            {
                product_column: df[product_column],
                value_column: _safe_numeric(df, value_column),
            }
        ).dropna()

        if not product_df.empty:
            product_df = (
                product_df
                .groupby(product_column, as_index=False)[value_column]
                .sum()
                .sort_values(
                    value_column,
                    ascending=False,
                )
                .head(12)
            )

            if not product_df.empty:
                figure = px.bar(
                    product_df,
                    x=product_column,
                    y=value_column,
                )

                # IMPORTANT:
                # Existing test expects "Top product".
                charts.append(
                    {
                        "id": f"product_{product_column}_{value_column}",
                        "title": f"Top {product_column} by {value_column}",
                        "figure": figure,
                    }
                )

    # ---------------------------------------------------------
    # 5. Category comparison
    # ---------------------------------------------------------
    category_column = _find_column(
        df,
        (
            "category",
            "segment",
            "type",
        ),
        exclude=set(date_columns),
    )

    if category_column and value_column:
        category_df = pd.DataFrame(
            {
                category_column: df[category_column],
                value_column: _safe_numeric(df, value_column),
            }
        ).dropna()

        if not category_df.empty:
            category_df = (
                category_df
                .groupby(category_column, as_index=False)[value_column]
                .sum()
                .sort_values(
                    value_column,
                    ascending=False,
                )
                .head(12)
            )

            if not category_df.empty:
                figure = px.bar(
                    category_df,
                    x=category_column,
                    y=value_column,
                )

                charts.append(
                    {
                        "id": f"category_{category_column}_{value_column}",
                        "title": f"Top {category_column} by {value_column}",
                        "figure": figure,
                    }
                )

    # ---------------------------------------------------------
    # 6. Region comparison
    # ---------------------------------------------------------
    region_column = _find_column(
        df,
        (
            "region",
            "area",
            "territory",
            "location",
        ),
        exclude=set(date_columns),
    )

    if region_column and value_column:
        region_df = pd.DataFrame(
            {
                region_column: df[region_column],
                value_column: _safe_numeric(df, value_column),
            }
        ).dropna()

        if not region_df.empty:
            region_df = (
                region_df
                .groupby(region_column, as_index=False)[value_column]
                .sum()
                .sort_values(
                    value_column,
                    ascending=False,
                )
                .head(12)
            )

            if not region_df.empty:
                figure = px.bar(
                    region_df,
                    x=region_column,
                    y=value_column,
                )

                charts.append(
                    {
                        "id": f"region_{region_column}_{value_column}",
                        "title": f"Top {region_column} by {value_column}",
                        "figure": figure,
                    }
                )

    # ---------------------------------------------------------
    # 7. Profitability
    # ---------------------------------------------------------
    profit_column = _find_column(
        df,
        (
            "profit",
            "margin",
            "earnings",
        ),
    )

    if (
        profit_column
        and value_column
        and profit_column != value_column
        and (
            "profit" in query_text
            or "margin" in query_text
            or "profitability" in query_text
        )
    ):
        profit_df = pd.DataFrame(
            {
                profit_column: _safe_numeric(df, profit_column),
                value_column: _safe_numeric(df, value_column),
            }
        ).dropna()

        if not profit_df.empty:
            figure = px.scatter(
                profit_df,
                x=value_column,
                y=profit_column,
            )

            charts.append(
                {
                    "id": f"profitability_{value_column}_{profit_column}",
                    "title": (
                        f"Profitability — "
                        f"{value_column} vs {profit_column}"
                    ),
                    "figure": figure,
                }
            )

    # ---------------------------------------------------------
    # 8. Correlation / relationship
    # ---------------------------------------------------------
    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    if (
        len(numeric_columns) >= 2
        and (
            "correlation" in query_text
            or "relationship" in query_text
            or "compare" in query_text
        )
    ):
        first_column = numeric_columns[0]
        second_column = numeric_columns[1]

        correlation_df = pd.DataFrame(
            {
                first_column: _safe_numeric(df, first_column),
                second_column: _safe_numeric(df, second_column),
            }
        ).dropna()

        if len(correlation_df) >= 2:
            figure = px.scatter(
                correlation_df,
                x=first_column,
                y=second_column,
            )

            charts.append(
                {
                    "id": f"scatter_{first_column}_{second_column}",
                    "title": (
                        f"Relationship — "
                        f"{first_column} vs {second_column}"
                    ),
                    "figure": figure,
                }
            )

    # ---------------------------------------------------------
    # 9. Categorical distribution fallback
    # ---------------------------------------------------------
    if not charts:
        categorical_columns = [
            column
            for column in df.columns
            if column not in date_columns
            and not pd.api.types.is_numeric_dtype(df[column])
        ]

        if categorical_columns:
            category = categorical_columns[0]

            counts = (
                df[category]
                .dropna()
                .value_counts()
                .head(15)
                .reset_index()
            )

            counts.columns = [
                category,
                "count",
            ]

            if not counts.empty:
                figure = px.bar(
                    counts,
                    x=category,
                    y="count",
                )

                charts.append(
                    {
                        "id": f"distribution_{category}",
                        "title": f"Distribution — {category}",
                        "figure": figure,
                    }
                )

    # ---------------------------------------------------------
    # 10. Numeric histogram fallback
    # ---------------------------------------------------------
    if not charts and numeric_columns:
        numeric_column = numeric_columns[0]

        numeric_values = (
            _safe_numeric(df, numeric_column)
            .dropna()
        )

        if not numeric_values.empty:
            histogram_df = pd.DataFrame(
                {
                    numeric_column: numeric_values,
                }
            )

            figure = px.histogram(
                histogram_df,
                x=numeric_column,
            )

            charts.append(
                {
                    "id": f"histogram_{numeric_column}",
                    "title": f"Distribution — {numeric_column}",
                    "figure": figure,
                }
            )

    return charts[:max_charts]
