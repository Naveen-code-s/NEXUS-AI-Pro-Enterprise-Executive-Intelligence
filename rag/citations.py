def citations(sources):
    out = []
    for s in sources or []:
        if not isinstance(s, dict):
            continue
        out.append({
            "source_id": s.get("source_id", "unknown"),
            "title": s.get("title") or s.get("filename") or "Not available",
            "filename": s.get("filename"),
            "page": s.get("page"),
            "provider": s.get("provider", "Unknown"),
            "source_type": s.get("source_type", "Unknown"),
            "url": s.get("url"),
            "doi": s.get("doi"),
            "passage": s.get("passage") or s.get("abstract") or "Evidence not available",
            "year": s.get("year"),
        })
    return out
