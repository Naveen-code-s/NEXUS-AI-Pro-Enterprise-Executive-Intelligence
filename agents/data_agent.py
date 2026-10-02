from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from analytics.data_analyzer import load, analyze
from analytics.visualizer import build_charts


class DataAgent:
    """
    NEXUS AI Data Intelligence Agent.

    Responsibilities:
    - Load CSV/XLSX datasets.
    - Run deterministic analytics.
    - Generate charts.
    - Detect data-quality issues.
    - Convert calculated findings into traceable evidence.
    - Preserve dataset/source information for downstream verification,
      citation, reasoning, and reporting.

    Public API intentionally remains:
        DataAgent().run(path, query)
    """

    name = "Data Intelligence"

    def run(self, path: str | Path, query: str) -> dict[str, Any]:
        """
        Analyze one dataset and return a complete intelligence package.

        The returned dictionary is consumed by the orchestrator and UI.
        """

        dataset_path = Path(path)

        if not dataset_path.exists():
            raise FileNotFoundError(
                f"Dataset file was not found: {dataset_path}"
            )

        df = load(dataset_path)

        if df is None:
            raise ValueError("Dataset loader returned no dataframe.")

        if df.empty:
            raise ValueError(
                f"The dataset '{dataset_path.name}' contains no rows."
            )

        result = analyze(df, query)

        if not isinstance(result, dict):
            raise ValueError(
                "Data analyzer returned an invalid result."
            )

        # ---------------------------------------------------------
        # Visualization
        # ---------------------------------------------------------
        try:
            charts = build_charts(df, query)
        except Exception:
            # Analytics should still work even if chart generation
            # fails for a specific dataset/query.
            charts = []

        result["charts"] = charts

        # ---------------------------------------------------------
        # Data quality
        # ---------------------------------------------------------
        result["data_quality"] = self._quality(df)

        # ---------------------------------------------------------
        # Source identity
        # ---------------------------------------------------------
        result["source"] = dataset_path.name
        result["source_path"] = str(dataset_path)

        # ---------------------------------------------------------
        # Dataset metadata
        # ---------------------------------------------------------
        result["dataset_metadata"] = self._metadata(df, dataset_path)

        # Keep dataframe available for downstream operations.
        result["dataframe"] = df

        # ---------------------------------------------------------
        # Traceable calculated evidence
        # ---------------------------------------------------------
        result["evidence"] = self._evidence(
            result=result,
            df=df,
            filename=dataset_path.name,
        )

        # ---------------------------------------------------------
        # Human-readable answer
        # ---------------------------------------------------------
        result["answer"] = self._answer(result, query)

        return result

    # =============================================================
    # DATA QUALITY
    # =============================================================

    @staticmethod
    def _quality(df: pd.DataFrame) -> list[str]:
        """
        Detect practical dataset-quality issues.

        No fabricated quality claims are produced.
        """

        issues: list[str] = []

        # Missing values
        missing = df.isna().sum()

        for column, count in missing[missing > 0].items():
            issues.append(
                f"{column}: {int(count):,} missing value(s)."
            )

        # Duplicate rows
        duplicated = int(df.duplicated().sum())

        if duplicated:
            issues.append(
                f"{duplicated:,} duplicate row(s) detected."
            )

        # Empty columns
        empty_columns = [
            str(column)
            for column in df.columns
            if df[column].isna().all()
        ]

        for column in empty_columns:
            issues.append(
                f"{column}: column contains no usable values."
            )

        # Constant columns
        constant_columns = []

        for column in df.columns:
            try:
                if df[column].nunique(dropna=True) <= 1:
                    constant_columns.append(str(column))
            except Exception:
                continue

        for column in constant_columns[:5]:
            issues.append(
                f"{column}: column has only one distinct non-null value."
            )

        if not issues:
            return [
                "No missing values, duplicate rows, empty columns, "
                "or constant-value issues were detected."
            ]

        return issues[:20]

    # =============================================================
    # DATASET METADATA
    # =============================================================

    @staticmethod
    def _metadata(
        df: pd.DataFrame,
        path: Path,
    ) -> dict[str, Any]:
        """
        Build deterministic metadata about the uploaded dataset.
        """

        numeric_columns = [
            str(column)
            for column in df.select_dtypes(include="number").columns
        ]

        categorical_columns = [
            str(column)
            for column in df.select_dtypes(exclude="number").columns
        ]

        try:
            file_size = path.stat().st_size
        except OSError:
            file_size = None

        return {
            "filename": path.name,
            "file_type": path.suffix.lower().replace(".", ""),
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "column_names": [str(column) for column in df.columns],
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns,
            "missing_cells": int(df.isna().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum()),
            "file_size_bytes": file_size,
        }

    # =============================================================
    # TRACEABLE EVIDENCE
    # =============================================================

    @staticmethod
    def _evidence(
        result: dict[str, Any],
        df: pd.DataFrame,
        filename: str,
    ) -> list[dict[str, Any]]:
        """
        Convert deterministic analytics into structured evidence.

        Important:
        These records represent calculations performed on the uploaded
        dataset. They are not external claims and should never be treated
        as external citations.

        Every evidence record contains:
        - source identity
        - evidence type
        - claim
        - calculation basis
        - relevant columns when available
        - metric/value when available
        """

        source_id = f"dataset:{filename}"

        evidence: list[dict[str, Any]] = []

        summary = result.get("summary", {})

        # ---------------------------------------------------------
        # Dataset shape evidence
        # ---------------------------------------------------------

        rows = summary.get("rows", len(df))
        columns = summary.get("columns", len(df.columns))

        evidence.append(
            {
                "source_id": source_id,
                "source_type": "dataset",
                "evidence_type": "calculated_dataset",
                "filename": filename,
                "title": filename,
                "claim": (
                    f"The dataset contains {int(rows):,} rows "
                    f"and {int(columns):,} columns."
                ),
                "basis": (
                    "Calculated directly from the uploaded dataframe "
                    "shape using row and column counts."
                ),
                "columns": [str(column) for column in df.columns],
                "row_count": int(len(df)),
                "column_count": int(len(df.columns)),
            }
        )

        # ---------------------------------------------------------
        # Missing-data evidence
        # ---------------------------------------------------------

        missing_cells = summary.get(
            "missing",
            int(df.isna().sum().sum()),
        )

        evidence.append(
            {
                "source_id": source_id,
                "source_type": "dataset",
                "evidence_type": "calculated_dataset",
                "filename": filename,
                "title": filename,
                "claim": (
                    f"The dataset contains {int(missing_cells):,} "
                    "missing cell(s)."
                ),
                "basis": (
                    "Calculated by counting null/missing values "
                    "across all dataframe columns."
                ),
                "metric": "Missing cells",
                "value": int(missing_cells),
            }
        )

        # ---------------------------------------------------------
        # Numeric / categorical field evidence
        # ---------------------------------------------------------

        numeric_columns = summary.get("numeric", [])

        categorical_columns = summary.get("categorical", [])

        evidence.append(
            {
                "source_id": source_id,
                "source_type": "dataset",
                "evidence_type": "calculated_dataset",
                "filename": filename,
                "title": filename,
                "claim": (
                    f"The dataset contains {len(numeric_columns)} "
                    f"numeric field(s) and "
                    f"{len(categorical_columns)} categorical field(s)."
                ),
                "basis": (
                    "Column data types were determined from the loaded "
                    "pandas dataframe."
                ),
                "metric": "Column types",
                "numeric_columns": list(numeric_columns),
                "categorical_columns": list(categorical_columns),
            }
        )

        # ---------------------------------------------------------
        # Calculated metrics
        # ---------------------------------------------------------

        metrics = result.get("metrics", {})

        if isinstance(metrics, dict):

            for label, value in metrics.items():

                if label in {
                    "Rows",
                    "Columns",
                    "Missing cells",
                }:
                    continue

                evidence.append(
                    {
                        "source_id": source_id,
                        "source_type": "dataset",
                        "evidence_type": "calculated_dataset",
                        "filename": filename,
                        "title": filename,
                        "claim": f"{label}: {value}",
                        "basis": (
                            "Calculated directly from observed values "
                            "in the uploaded dataset."
                        ),
                        "metric": str(label),
                        "value": DataAgent._safe_value(value),
                    }
                )

        # ---------------------------------------------------------
        # Analytical insights
        # ---------------------------------------------------------

        insights = result.get("insights", [])

        if isinstance(insights, list):

            for insight in insights:

                if not insight:
                    continue

                evidence.append(
                    {
                        "source_id": source_id,
                        "source_type": "dataset",
                        "evidence_type": "calculated_dataset",
                        "filename": filename,
                        "title": filename,
                        "claim": str(insight),
                        "basis": (
                            "Derived by NEXUS deterministic analytics "
                            "from observed rows and columns in the "
                            "uploaded dataset."
                        ),
                    }
                )

        # ---------------------------------------------------------
        # Data-quality evidence
        # ---------------------------------------------------------

        quality = result.get("data_quality", [])

        if isinstance(quality, list):

            for issue in quality:

                if not issue:
                    continue

                evidence.append(
                    {
                        "source_id": source_id,
                        "source_type": "dataset",
                        "evidence_type": "calculated_dataset",
                        "filename": filename,
                        "title": filename,
                        "claim": str(issue),
                        "basis": (
                            "Calculated from dataset completeness, "
                            "duplicate-row, empty-column, and "
                            "constant-value checks."
                        ),
                    }
                )

        # ---------------------------------------------------------
        # Add dataset-level provenance to every evidence record
        # ---------------------------------------------------------

        for item in evidence:

            item.setdefault("dataset_rows", int(len(df)))
            item.setdefault(
                "dataset_columns",
                [str(column) for column in df.columns],
            )

        # Keep the evidence payload bounded for downstream agents.
        return evidence[:40]

    # =============================================================
    # HUMAN-READABLE ANSWER
    # =============================================================

    @staticmethod
    def _answer(
        result: dict[str, Any],
        query: str,
    ) -> str:
        """
        Build a deterministic summary for the orchestration layer.

        The LLM can later synthesize this result, but this function
        itself does not invent business conclusions.
        """

        summary = result.get("summary", {})

        rows = summary.get("rows", 0)
        columns = summary.get("columns", 0)
        numeric = summary.get("numeric", [])
        categorical = summary.get("categorical", [])
        missing = summary.get("missing", 0)

        source = result.get("source", "uploaded dataset")

        lines = [
            (
                f"Dataset **{source}** contains "
                f"{int(rows):,} rows across {int(columns):,} columns."
            ),
            (
                f"Detected {len(numeric)} numeric field(s) and "
                f"{len(categorical)} categorical field(s), "
                f"with {int(missing):,} missing cell(s)."
            ),
        ]

        # Add deterministic findings only.
        insights = result.get("insights", [])

        if isinstance(insights, list) and insights:
            clean_insights = [
                str(item)
                for item in insights[:8]
                if item
            ]

            if clean_insights:
                lines.append(
                    "Key analytical findings: "
                    + " ".join(clean_insights)
                )

        # Data quality summary.
        quality = result.get("data_quality", [])

        if isinstance(quality, list) and quality:
            lines.append(
                "Data quality observations: "
                + " ".join(str(item) for item in quality[:5])
            )

        return "\n\n".join(lines)

    # =============================================================
    # SAFE VALUE NORMALIZATION
    # =============================================================

    @staticmethod
    def _safe_value(value: Any) -> Any:
        """
        Convert pandas/numpy scalar values into JSON-friendly Python
        values where possible.
        """

        if value is None:
            return None

        # pandas scalar handling
        try:
            if pd.isna(value):
                return None
        except (TypeError, ValueError):
            pass

        # numpy/pandas numeric scalars
        try:
            if hasattr(value, "item"):
                return value.item()
        except (ValueError, TypeError):
            pass

        # Simple JSON-safe primitives
        if isinstance(
            value,
            (str, int, float, bool),
        ):
            return value

        return str(value)