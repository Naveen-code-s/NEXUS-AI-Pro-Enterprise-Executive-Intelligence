from search.local import search as local_search
from search.providers import semantic,openalex,crossref
def dedup(items):
    seen=set(); out=[]
    for x in items:
        key=(x.get("doi") or x.get("title") or "").lower().strip()
        if key and key not in seen:seen.add(key);out.append(x)
    return out
def search_global(settings,q,local=True,external=True,limit=6):
    out=[]
    if local: out+=local_search(settings,q,limit)
    if external: out+=semantic(settings,q,limit)+openalex(settings,q,limit)+crossref(settings,q,limit)
    return dedup(out)[:limit*2]
