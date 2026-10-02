"""
NEXUS AI - Evidence Verification Agent

Responsible for classifying retrieved evidence into:
    - Direct evidence
    - Calculated evidence
    - Related evidence
    - Insufficient evidence
    - Conflicting evidence

Important:
- Dataset-derived calculations are treated as first-class evidence.
- Document evidence is evaluated from retrieved text.
- External research evidence can retain title/author/year/DOI/URL metadata.
- The verifier does not invent citations or evidence.
"""

from __future__ import annotations

import re
from typing import Any


class VerificationAgent:
    """
    Verifies whether retrieved sources support a user's request.

    The method signature intentionally remains:

        VerificationAgent().run(query, sources)

    so the existing orchestrator does not need to change.
    """

    name = "Evidence Verification"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, query: str, sources: Any) -> list[dict[str, Any]]:
        """
        Verify a collection of evidence sources.

        Parameters
        ----------
        query:
            User's original request/question.

        sources:
            Retrieved evidence objects. Each item should normally be a dict.

        Returns
        -------
        list[dict[str, Any]]
            Normalized verification results.
        """

        clean_sources = self._normalize_sources(sources)

        if not clean_sources:
            return [
                self._insufficient(
                    reason="No evidence sources were retrieved."
                )
            ]

        query_terms = self._query_terms(query)
        results: list[dict[str, Any]] = []

        for raw_source in clean_sources:
            source = self._normalize_source(raw_source)

            # Dataset calculations are deterministic evidence.
            if self._is_calculated_dataset_evidence(source):
                results.append(
                    self._verify_calculated_dataset(source)
                )
                continue

            # Explicit conflict information, when produced by another
            # component, is preserved rather than silently overridden.
            if self._is_conflicting_source(source):
                results.append(
                    self._verify_conflict(source)
                )
                continue

            # Normal document / research evidence.
            results.append(
                self._verify_text_evidence(
                    source=source,
                    query_terms=query_terms,
                )
            )

        return results

    # ------------------------------------------------------------------
    # Source normalization
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_sources(sources: Any) -> list[Any]:
        """Safely normalize the incoming source collection."""

        if sources is None:
            return []

        if isinstance(sources, dict):
            return [sources]

        if isinstance(sources, (list, tuple)):
            return list(sources)

        return []

    @staticmethod
    def _normalize_source(source: Any) -> dict[str, Any]:
        """
        Convert unexpected source objects into a safe dictionary.

        This prevents verification from crashing when an upstream agent
        accidentally returns a non-dict object.
        """

        if isinstance(source, dict):
            return source

        # Some retrieval libraries expose document-like objects.
        metadata = getattr(source, "metadata", None)

        if isinstance(metadata, dict):
            text = getattr(source, "page_content", None)

            normalized = dict(metadata)

            if text and not any(
                normalized.get(key)
                for key in ("passage", "snippet", "abstract", "text")
            ):
                normalized["passage"] = text

            return normalized

        return {}

    # ------------------------------------------------------------------
    # Query processing
    # ------------------------------------------------------------------

    @staticmethod
    def _query_terms(query: str) -> set[str]:
        """
        Extract useful query terms.

        Very short/common words are ignored to reduce accidental matches.
        """

        stop_words = {
            "what",
            "when",
            "where",
            "which",
            "with",
            "from",
            "that",
            "this",
            "into",
            "have",
            "has",
            "will",
            "would",
            "could",
            "should",
            "about",
            "show",
            "give",
            "find",
            "tell",
            "please",
            "make",
            "create",
            "analyze",
            "analysis",
            "explain",
            "clearly",
        }

        words = re.findall(r"\b[a-zA-Z0-9_]+\b", query or "")

        return {
            word.lower()
            for word in words
            if len(word) > 3 and word.lower() not in stop_words
        }

    # ------------------------------------------------------------------
    # Dataset evidence
    # ------------------------------------------------------------------

    @staticmethod
    def _is_calculated_dataset_evidence(
        source: dict[str, Any],
    ) -> bool:
        """Identify first-class evidence generated from uploaded datasets."""

        return (
            source.get("source_type") == "dataset"
            and source.get("evidence_type") == "calculated_dataset"
        )

    def _verify_calculated_dataset(
        self,
        source: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Verify deterministic calculations from uploaded CSV/XLSX data.

        These findings are not required to appear as literal sentences
        inside the source file. Their evidence basis is the observed
        dataset values and the calculation performed by NEXUS.
        """

        claim = str(
            source.get("claim")
            or source.get("description")
            or "Calculated dataset finding"
        )

        basis = str(
            source.get("basis")
            or "Calculated directly from observed uploaded dataset values."
        )

        filename = source.get("filename")
        columns = self._as_list(source.get("columns"))
        metric = source.get("metric")
        value = source.get("value")

        source_label = (
            str(filename)
            if filename
            else str(source.get("source_id") or "uploaded dataset")
        )

        reason = (
            f"{claim} "
            f"Evidence is calculated directly from the observed values "
            f"in {source_label}. {basis}"
        )

        return {
            "source_id": source.get("source_id", "dataset"),
            "level": "Calculated evidence",
            "reason": reason,
            "claim": claim,
            "basis": basis,
            "filename": filename,
            "source_type": "dataset",
            "evidence_type": "calculated_dataset",
            "columns": columns,
            "metric": metric,
            "value": value,
            "page": source.get("page"),
            "title": source.get("title") or filename,
            "verification_method": "deterministic_dataset_calculation",
        }

    # ------------------------------------------------------------------
    # Text/document/research evidence
    # ------------------------------------------------------------------

    def _verify_text_evidence(
        self,
        source: dict[str, Any],
        query_terms: set[str],
    ) -> dict[str, Any]:
        """
        Verify document or research evidence using retrieved text.

        This intentionally does not fabricate support. If there is no
        retrievable text, the result remains insufficient.
        """

        text = self._source_text(source)

        if not text:
            return self._insufficient(
                source=source,
                reason="The source contains no retrievable evidence text.",
            )

        text_terms = set(
            re.findall(r"\b[a-zA-Z0-9_]+\b", text.lower())
        )

        overlap = len(query_terms & text_terms)

        # Exact/strong overlap threshold.
        direct_threshold = self._direct_threshold(
            len(query_terms)
        )

        if overlap >= direct_threshold:
            level = "Direct evidence"
            reason = (
                f"The retrieved evidence contains {overlap} "
                f"query-relevant terms and directly supports the requested "
                f"topic."
            )

        elif overlap > 0:
            level = "Related evidence"
            reason = (
                f"The retrieved evidence is related, but textual support "
                f"is partial ({overlap} matching terms)."
            )

        else:
            level = "Insufficient evidence"
            reason = (
                "The retrieved text does not contain sufficient "
                "query-relevant support for the requested claim."
            )

        return {
            "source_id": source.get("source_id", "unknown"),
            "level": level,
            "reason": reason,
            "filename": source.get("filename"),
            "page": source.get("page"),
            "title": source.get("title") or source.get("filename"),
            "source_type": source.get("source_type"),
            "evidence_type": source.get("evidence_type"),
            "verification_method": "retrieved_text_overlap",
            "matched_terms": overlap,
            "query_terms": sorted(query_terms),
        }

    # ------------------------------------------------------------------
    # Conflict evidence
    # ------------------------------------------------------------------

    @staticmethod
    def _is_conflicting_source(
        source: dict[str, Any],
    ) -> bool:
        """
        Detect explicit conflict metadata from upstream research agents.

        We only classify something as conflicting when another component
        explicitly marked it as such. We do not invent conflicts.
        """

        return bool(
            source.get("conflict") is True
            or source.get("evidence_level") == "conflict"
            or source.get("verification_status") == "conflict"
        )

    def _verify_conflict(
        self,
        source: dict[str, Any],
    ) -> dict[str, Any]:
        """Preserve an explicitly identified conflict."""

        return {
            "source_id": source.get("source_id", "unknown"),
            "level": "Conflicting evidence",
            "reason": str(
                source.get("conflict_reason")
                or source.get("reason")
                or "The source was explicitly marked as conflicting."
            ),
            "filename": source.get("filename"),
            "page": source.get("page"),
            "title": source.get("title") or source.get("filename"),
            "source_type": source.get("source_type"),
            "evidence_type": source.get("evidence_type"),
            "verification_method": "explicit_conflict_metadata",
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _source_text(source: dict[str, Any]) -> str:
        """Extract textual evidence without assuming one fixed field."""

        candidates = (
            source.get("passage"),
            source.get("abstract"),
            source.get("snippet"),
            source.get("text"),
            source.get("content"),
            source.get("page_content"),
        )

        for value in candidates:
            if value is not None:
                text = str(value).strip()
                if text:
                    return text

        return ""

    @staticmethod
    def _direct_threshold(term_count: int) -> int:
        """
        Determine a conservative direct-evidence threshold.

        For very short queries, require at least two matching terms.
        For larger queries, require a meaningful subset.
        """

        if term_count <= 2:
            return 2

        if term_count <= 4:
            return 3

        return min(4, max(3, round(term_count * 0.5)))

    @staticmethod
    def _as_list(value: Any) -> list[Any]:
        """Normalize scalar/list values for UI-safe output."""

        if value is None:
            return []

        if isinstance(value, (list, tuple, set)):
            return list(value)

        return [value]

    @staticmethod
    def _insufficient(
        source: dict[str, Any] | None = None,
        reason: str = "Evidence is not available.",
    ) -> dict[str, Any]:
        """Create a consistent insufficient-evidence result."""

        source = source or {}

        return {
            "source_id": source.get("source_id", "none"),
            "level": "Insufficient evidence",
            "reason": reason,
            "filename": source.get("filename"),
            "page": source.get("page"),
            "title": source.get("title") or source.get("filename"),
            "source_type": source.get("source_type"),
            "evidence_type": source.get("evidence_type"),
            "verification_method": "no_sufficient_support",
        }