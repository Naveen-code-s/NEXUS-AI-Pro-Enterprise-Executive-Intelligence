import requests
def get(url,params):
    try:r=requests.get(url,params=params,timeout=12,headers={"User-Agent":"NEXUS-AI/0.1"}); r.raise_for_status(); return r.json()
    except Exception:return None
def semantic(settings,q,n=5):
    d=get(settings.semantic_scholar_api_url,{"query":q,"limit":n,"fields":"paperId,title,authors,year,abstract,url,externalIds,citationCount"}); out=[]
    for p in (d or {}).get("data",[]):
        ids=p.get("externalIds") or {}; out.append({"source_id":"semantic:"+str(p.get("paperId")),"title":p.get("title") or "Not available","source_type":"ACADEMIC","provider":"Semantic Scholar","url":p.get("url"),"doi":ids.get("DOI"),"authors":[a.get("name") for a in p.get("authors") or []],"year":p.get("year"),"abstract":p.get("abstract"),"citation_count":p.get("citationCount")})
    return out
def openalex(settings,q,n=5):
    d=get(settings.openalex_api_url,{"search":q,"per-page":n}); out=[]
    for p in (d or {}).get("results",[]): out.append({"source_id":"openalex:"+str(p.get("id")),"title":p.get("display_name") or "Not available","source_type":"ACADEMIC","provider":"OpenAlex","url":p.get("doi") or p.get("id"),"doi":p.get("doi"),"year":p.get("publication_year"),"citation_count":p.get("cited_by_count")})
    return out
def crossref(settings,q,n=5):
    d=get(settings.crossref_api_url,{"query.bibliographic":q,"rows":n}); out=[]
    for p in (d or {}).get("message",{}).get("items",[]): out.append({"source_id":"crossref:"+str(p.get("DOI") or p.get("title")),"title":(p.get("title") or ["Not available"])[0],"source_type":"ACADEMIC","provider":"Crossref","url":p.get("URL"),"doi":p.get("DOI"),"year":None})
    return out
